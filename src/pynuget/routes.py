# -*- coding: utf-8 -*-
"""
"""
import base64
import hashlib
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as et
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

# Third-Party
from flask import g
from flask import request
from flask import make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from werkzeug.local import LocalProxy

from pynuget import app
from pynuget import db
from pynuget import core
from pynuget import logger
from pynuget.feedwriter import FeedWriter
from pynuget.core import et_to_str
from pynuget.core import ApiException


FEED_CONTENT_TYPE_HEADER = 'application/atom+xml; type=feed; charset=UTF-8'


def get_db_session():
    session = getattr(g, 'session', None)
    if session is None:
        # TODO: Handle MySQL/PostgreSQL backends.
        db_name = Path(app.config['SERVER_PATH']) / Path(app.config['DB_NAME'])

        # TODO: Move this check so that it gets run on server start, not
        # just when a route that uses the session is called.
        if not db_name.exists():
            msg = "'{}' does not exist. Did you forget to run pynuget init?"
            msg = msg.format(str(db_name))
            logger.critical(msg)
            raise FileNotFoundError(msg)

        url = "sqlite:///{}".format(str(db_name))
        engine = create_engine(url, echo=False)
        Session = sessionmaker(bind=engine)
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
    logger.debug("Route: /web")
    return "Hello World!"


@app.route('/', methods=['GET', 'PUT', 'DELETE'])
@app.route('/index', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/v2/package/', methods=['GET', 'PUT', 'DELETE'])
def index():
    logger.debug("Route: /index")
    if request.method == 'PUT':
        return push()

    resp = make_response(
        "<?xml version='1.0' encoding='utf-8' standalone='yes'?>",
    )
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


def push():
    logger.debug("push()")
    if not core.require_auth(request.headers):
        return "api_error: Missing or Invalid API key"      # TODO

    logger.debug("Checking for uploaded file.")
    if 'package' not in request.files:
        logger.error("Package file was not uploaded.")
        return "error: File not uploaded"
    file = request.files['package']

    # Open the zip file that was sent and extract out the .nuspec file."
    try:
        nuspec = core.extract_nuspec(file)
    except Exception as err:
        logger.error("Exception: %s" % err)
        return "api_error: Zero or multiple nuspec files found"

    # The NuSpec XML file uses namespaces.
    # TODO: What if the namespace changes?
    ns = {'nuspec': 'http://schemas.microsoft.com/packaging/2012/06/nuspec.xsd'}

    # Make sure both the ID and the version are provided in the .nuspec file.
    try:
        metadata, pkg_name, version = core.parse_nuspec(nuspec, ns)
    except ApiException as err:
        return str(err)
    except Exception:
        raise

    valid_id = re.compile('^[A-Z0-9\.\~\+\_\-]+$', re.IGNORECASE)

    # Make sure that the ID and version are sane
    if not re.match(valid_id, pkg_name) or not re.match(valid_id, version):
        logger.error("Invalid ID or version.")
        return "api_error: Invlaid ID or Version"      # TODO

    # and that we don't already have that ID+version in our database
    if db.validate_id_and_version(session, pkg_name, version):
        logger.error("Package %s version %s already exists" % (pkg_name, version))
        return "api_error: Package version already exists"      # TODO

    # Hash the uploaded file and encode the hash in Base64. For some reason.
    try:
        hash_, filesize = core.hash_and_encode_file(file, pkg_name, version)
    except Exception as err:
        logger.error("Exception: %s" % err)
        return "api_error: Unable to save file"

    try:
        dependencies = core.determine_dependencies(metadata, ns)
    except Exception as err:
        logger.error("Exception: %s" % err)
        return "api_error: Unable to parse dependencies."

    logger.debug(dependencies)

    # and finaly, update our database.
    logger.debug("Updating database entries.")

    db.insert_or_update_package(session,
                                name=pkg_name,
                                title=et_to_str(metadata.find('nuspec:title', ns)),
                                latest_version=version)
    pkg_id = session.query(db.Package).filter(name=pkg_name).one()
    db.insert_version(
        session,
        authors=et_to_str(metadata.find('nuspec:authors', ns)),
        copyright_=et_to_str(metadata.find('nuspec:copyright', ns)),
        dependencies=dependencies,
        description=et_to_str(metadata.find('nuspec:description', ns)),
        package_hash=hash_,
        package_hash_algorithm='SHA512',
        package_size=filesize,
        icon_url=et_to_str(metadata.find('nuspec:iconUrl', ns)),
        is_prerelease='-' in version,
        license_url=et_to_str(metadata.find('nuspec:licenseUrl', ns)),
        owners=et_to_str(metadata.find('nuspec:owners', ns)),
        package_id=pkg_id,
        project_url=et_to_str(metadata.find('nuspec:projectUrl', ns)),
        release_notes=et_to_str(metadata.find('nuspec:releaseNotes', ns)),
        require_license_acceptance=et_to_str(metadata.find('nuspec:requireLicenseAcceptance', ns)) == 'true',
        tags=et_to_str(metadata.find('nuspec:tags', ns)),
        title=et_to_str(metadata.find('nuspec:title', ns)),
        version=version,
    )

    logger.info("Sucessfully updated database entries for package %s version %s." % (pkg_name, version))

    resp = make_response('', 201)
    return resp


@app.route('/count', methods=['GET'])
def count():
    logger.debug("Route: /count")
    resp = make_response(str(db.count_packages(session)))
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


@app.route('/delete', methods=['DELETE'])
@app.route('/api/v2/package/<package>/<version>', methods=['DELETE'])
def delete(package=None, version=None):
    logger.debug("Route: /delete")
    if not core.require_auth(request.headers):
        return "api_error: Missing or Invalid API key"      # TODO

    if package is not None:
        id_ = package
    else:
        id_ = request.args.get('id')

    if version is None:
        version = request.args.get('version')
    path = core.get_package_path(id_, version)

    if os.path.exists(path):
        os.remove(path)

    try:
        db.delete_version(session, id_, version)
    except NoResultFound:
        raise ApiException("Package %s version %s not found." % (id_, version))

    logger.info("Sucessfully deleted package %s version %s." % (id_, version))


@app.route('/download', methods=['GET'])
def download():
    logger.debug("Route: /download")
    id_ = request.args.get('id')
    version = request.args.get('version')

    path = core.get_package_path(id_, version)
    db.increment_download_count(session, id_, version)
    filename = "{}.{}.nupkg".format(id_, version)

    resp = make_response()
    resp.headers[''] = 'application/zip'
    resp.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    resp.headers['X-Accel-Redirect'] = path

    return resp


@app.route('/find_by_id', methods=['GET'])
def find_by_id():
    logger.debug("Route: /find_by_id")
    id_ = request.args.get('id')
    version = request.args.get('version', default=None)

    results = db.find_by_id(id_, version)
    feed = FeedWriter('FindPackagesById')
    resp = make_response(feed.write_to_output(results))
    resp.headers['Content-Type']
    return resp


@app.route('/search', methods=['GET'])
def search():
    logger.debug("Route: /search")
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
    resp = make_response(feed.write_to_output(results))
    resp.headers['Content-Type'] = FEED_CONTENT_TYPE_HEADER
    return resp


@app.route('/updates', methods=['GET'])
def updates():
    logger.debug("Route: /updates")
    ids = request.args.get('packageids').strip("'").split('|')
    versions = request.args.get('versions').strip("'").split('|')
    include_prerelease = request.args.get('includeprerelease', default=False)
    pkg_to_vers = {k: v for k, v in zip(ids, versions)}

    results = db.package_updates(session, pkg_to_vers, include_prerelease)

    feed = FeedWriter('GetUpdates')
    resp = make_response(feed.write_to_output(results))
    resp.headers['Content-Type'] = FEED_CONTENT_TYPE_HEADER
    return resp
