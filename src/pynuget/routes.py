# -*- coding: utf-8 -*-
"""
"""
import base64
import hashlib
import os
import re
import xml.etree.ElementTree as et
from zipfile import ZipFile

# Third-Party
from flask import g
from flask import request
from flask import Response
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from werkzeug.local import LocalProxy

from pynuget import app
from pynuget import db
from pynuget import core
from pynuget.feedwriter import FeedWriter


FEED_CONTENT_TYPE_HEADER = 'application/atom+xml; type=feed; charset=UTF-8'


def get_db_session():
    session = getattr(g, 'session', None)
    if session is None:
        # TODO: Handle pre-existing DB files.
        # TODO: Use files not memory
        engine = create_engine('sqlite:///:memory:', echo=False)
        Session = sessionmaker(bind=engine)
        db.Base.metadata.create_all(engine)
        session = g.session = Session()
    return session


@app.teardown_appcontext
def teardown_db_session(exception):
    session = getattr(g, 'session', None)
    if session is not None:
        session.close()


session = LocalProxy(get_db_session)


@app.route('/web')
def root():
    return "Hello World!"


@app.route('/', methods=['GET', 'PUT', 'DELETE'])
@app.route('/index', methods=['GET', 'PUT', 'DELETE'])
def index():
    if request.method == 'PUT':
        return push()

    resp = Response("<?xml version='1.0' encoding='utf-8' standalone='yes'?>")
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


def push():
    # TODO
    #core.require_auth()

    # TODO: `if 'file' not in request.files`
    file = request.files['file']
    pkg = ZipFile(file, 'r')

    # Open the zip file that was sent and extract out the .nuspec file."
    # TODO: Cleanup, python-ize
    nuspec_file = None
    if '.nuspec' not in pkg.namelist():
        return "api_error: nuspec file not found"      # TODO
    else:
        nuspec_file = "some.nuspec"

    with pkg.open(nuspec_file, 'r') as openf:
        nuspec_string = openf.read()

    nuspec = et.fromstring(nuspec_string)

    # TODO
    # Make sure both the ID and the version are provided in the .nuspec file.
    if nuspec['metadata']['id'] is None or nuspec['metadata']['version'] is None:
        return "api_error: ID or version missing"

    id_ = str(nuspec['metadata']['id'])
    version = str(nuspec['metadata']['version'])
    valid_id = re.compile('^[A-Z0-9\.\~\+\_\-]+$', re.IGNORECASE)

    # Make sure that the ID and version are sane
    if not re.match(valid_id, id_) or not re.match(valid_id, version):
        return "api_error: Invlaid ID or Version"      # TODO

    # and that we don't already have that ID+version in our database
    if db.validate_id_and_version(session, id_, version):
        return "api_error: Package version already exists"      # TODO

    # Hash the uploaded file and encode the hash in Base64. For some reason.
    m = hashlib.sha512()
    with open(file, 'r') as openf:
        m.update(openf.read())
    hash_ = base64.b64encode(m.digest())

    # Get the filesize of the uploaded file. Used later.
    filesize = os.path.getsize(file)

    # Determine dependencies.
    # TODO: python-ify
    dependencies = []
    if nuspec['metadata']['dependencies']:
        if nuspec['metadata']['dependencies']['dependency']:
            # Dependencies that are not specific to any framework
            for dependency in nuspec['metadata']['dependencies']['dependency']:
                d = {'framework': None,
                     'id': str(dependency['id']),
                     'version': str(dependency['version']),
                     }
                dependencies.append(d)
        if nuspec['metadata']['dependencies']['group']:
            # Dependencies that are specific to a particular framework
            for group in nuspec['metadata']['dependencies']['group']:
                for dependency in group['dependency']:
                    d = {'framework': str(group['targetFramework']),
                         'id': str(dependency['id']),
                         'version': str(dependency['version']),
                         }
                    dependencies.append(d)

    # Save the package file to the local package dir. Thus far it's just been
    # floating around in magic Flask land.
    # TODO: Custom dir
    local_path = "./packagefiles/{}/{}.nupkg".format(id_, version)

    # Check if the pacakge's directory already exists. Create if needed.
    os.makedirs(os.path.split(local_path)[0],
                mode=0o0755,
                exist_ok=True,      # do not throw an error path exists.
                )

    try:
        file.save(local_path)
    except Exception:       # TODO: specify exceptions
        return "api_error: Unable to save file"

    # and finaly, update our database.
    db.insert_or_update_package(session,
                                package_id=id_,
                                title=nuspec['metadata']['title'],
                                version=version)
    db.insert_version(
        session,
        authors=nuspec['metadata']['authors'],
        copyright_=nuspec['metadata']['copyright'],
        dependencies=dependencies,
        description=nuspec['metadata']['description'],
        package_hash=hash_,
        package_hash_algorithm='SHA512',
        pacakge_size=filesize,
        icon_url=nuspec['metadata']['iconUrl'],
        is_prerelease='-' in version,
        license_url=nuspec['metadata']['licenseUrl'],
        owners=nuspec['metadata']['owners'],
        package_id=id_,
        project_url=nuspec['metadata']['projectUrl'],
        release_notes=nuspec['metadata']['releaseNotes'],
        require_license_agreement=nuspec['metadata']['requireLicenseAcceptance'] == 'true',
        tags=nuspec['metadata']['tags'],
        title=nuspec['metadata']['title'],
        version=version,
    )

    resp = Response()
    resp.status = 201
    return resp


@app.route('/count', methods=['GET'])
def count():
    resp = Response(str(db.count_packages(session)))
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


@app.route('/delete', methods=['DELETE'])
def delete():
    #core.require_auth()
    id_ = request.args.get('id')
    version = request.args.get('version')
    path = core.get_package_path(id_, version)

    if os.path.exists(path):
        os.remove(path)

    db.delete_version(session, id_, version)


@app.route('/download', methods=['GET'])
def download():
    id_ = request.args.get('id')
    version = request.args.get('version')

    path = core.get_package_path(id_, version)
    db.increment_download_count(session, id_, version)
    filename = "{}.{}.nupkg".format(id_, version)

    resp = Response()
    resp.headers[''] = 'application/zip'
    resp.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    resp.headers['X-Accel-Redirect'] = path

    return resp


@app.route('/find_by_id', methods=['GET'])
def find_by_id():
    id_ = request.args.get('id')
    version = request.args.get('version', default=None)

    results = db.find_by_id(id_, version)
    feed = FeedWriter('FindPackagesById')
    resp = Response(feed.write_to_output(results))
    resp.headers['Content-Type']
    return resp


@app.route('/search', methods=['GET'])
def search():
    # TODO: Cleanup this and db.search_pacakges call sig.
    include_prerelease = request.args.get('includeprerelease', default=False)
    order_by = request.args.get('orderby', default=None)
    filter_ = request.args.get('filter', default=None)
    search_query = request.args.get('searchQuery', default=None)
    results = db.search_packages(session,
                                 include_prerelease,
                                 #order_by
                                 filter_,
                                 search_query,
                                 )

    feed = FeedWriter('Search')
    resp = Response(feed.write_to_output(results))
    resp.headers['Content-Type'] = FEED_CONTENT_TYPE_HEADER
    return resp


@app.route('/updates', methods=['GET'])
def updates():
    ids = request.args.get('packageids').strip("'").split('|')
    versions = request.args.get('versions').strip("'").split('|')
    include_prerelease = request.args.get('includeprerelease', default=False)
    pkg_to_vers = {k: v for k, v in zip(ids, versions)}

    results = db.package_updates(session, pkg_to_vers, include_prerelease)

    feed = FeedWriter('GetUpdates')
    resp = Response(feed.write_to_output(results))
    resp.headers['Content-Type'] = FEED_CONTENT_TYPE_HEADER
    return resp
