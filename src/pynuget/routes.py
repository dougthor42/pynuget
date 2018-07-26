# -*- coding: utf-8 -*-
"""
"""
import re
from pathlib import Path
from uuid import uuid4

# Third-Party
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import send_file
from flask import make_response
from flask import Blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from werkzeug.local import LocalProxy

from pynuget import db
from pynuget import core
from pynuget import logger
from pynuget.feedwriter import FeedWriter
from pynuget.core import et_to_str
from pynuget.core import ApiException


FEED_CONTENT_TYPE_HEADER = 'application/atom+xml; type=feed; charset=UTF-8'


pages = Blueprint('pages', __name__)


def get_db_session():
    session = getattr(g, 'session', None)
    if session is None:
        # TODO: Handle MySQL/PostgreSQL backends.
        db_name = Path(current_app.config['SERVER_PATH']) / Path(current_app.config['DB_NAME'])

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


session = LocalProxy(get_db_session)


@pages.route('/$metadata')
def meta():
    """
    The `nuget list` command calls this route.
    """
    logger.debug("route: /$metadata")
    resp = make_response(
        """<?xml version="1.0" encoding="utf-8"?>
        <service xml:base="{}" xmlns="http://www.w3.org/2007/app" xmlns:atom="http://www.w3.org/2005/Atom">
          <workspace>
            <atom:title type="text">Default</atom:title>
            <collection href="Packages">
              <atom:title type="text">Packages</atom:title>
            </collection>
          </workspace>
        </service>""".format(request.url_root)
    )
    resp.headers['Content-Type'] = 'application/atomsvc+xml; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '-1'

    logger.debug("Returning resp: %s" % str(resp))
    return resp


@pages.route('/', methods=['GET'])
@pages.route('/index', methods=['GET'])
def index():
    """
    Used for web interface.
    """
    logger.debug("Route: /index")
    version = "<TODO>"
    return render_template("web/index.html", server_version=version)


@pages.route('/api/v2/package/', methods=['PUT'])
def push():
    """
    Used by `nuget push`.
    """
    logger.debug("push()")
    logger.debug("  args: {}".format(request.args))
    logger.debug("  header: {}".format(request.headers))
    if not core.require_auth(request.headers):
        return "api_error: Missing or Invalid API key", 401

    logger.debug("Checking for uploaded file.")
    if 'package' not in request.files:
        logger.error("Package file was not uploaded.")
        return "error: File not uploaded", 409
    file = request.files['package']

    # Save the file to a temporary location
    file = core.save_file(file, "_temp", str(uuid4()))

    # Open the zip file that was sent and extract out the .nuspec file."
    try:
        nuspec = core.extract_nuspec(file)
    except Exception as err:
        logger.error("Exception: %s" % err)
        return "api_error: Zero or multiple nuspec files found", 400

    # The NuSpec XML file uses namespaces.
    ns = {'nuspec': core.extract_namespace(nuspec)}

    # Make sure both the ID and the version are provided in the .nuspec file.
    try:
        metadata, pkg_name, version = core.parse_nuspec(nuspec, ns)
    except ApiException as err:
        return str(err), 400
    except Exception as err:
        logger.error(err)
        return str(err), 400

    valid_id = re.compile('^[A-Z0-9\.\~\+\_\-]+$', re.IGNORECASE)

    # Make sure that the ID and version are sane
    if not re.match(valid_id, pkg_name) or not re.match(valid_id, version):
        logger.error("Invalid ID or version.")
        return "api_error: Invlaid ID or Version", 400

    # and that we don't already have that ID+version in our database
    if db.validate_id_and_version(session, pkg_name, version):
        logger.error("Package %s version %s already exists" % (pkg_name, version))
        return "api_error: Package version already exists", 409

    # Hash the uploaded file and encode the hash in Base64. For some reason.
    try:
        # rename our file.
        # Check if the package's directory already exists. Create if needed.
        new = file.parent.parent / pkg_name / (version + ".nupkg")
        core.create_parent_dirs(new)
        logger.debug("Renaming %s to %s" % (str(file), new))
        file.rename(new)
        hash_, filesize = core.hash_and_encode_file(str(new))
    except Exception as err:
        logger.error("Exception: %s" % err)
        return "api_error: Unable to save file", 500

    try:
        dependencies = core.determine_dependencies(metadata, ns)
    except Exception as err:
        logger.error("Exception: %s" % err)
        return "api_error: Unable to parse dependencies.", 400

    logger.debug(dependencies)

    # and finaly, update our database.
    logger.debug("Updating database entries.")

    db.insert_or_update_package(session,
                                package_name=pkg_name,
                                title=et_to_str(metadata.find('nuspec:title', ns)),
                                latest_version=version)
    pkg_id = (session.query(db.Package)
              .filter(db.Package.name == pkg_name).one()
              ).package_id
    logger.debug("package_id = %d" % pkg_id)
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
        title=et_to_str(metadata.find('nuspec:id', ns)),
        version=version,
    )

    logger.info("Sucessfully updated database entries for package %s version %s." % (pkg_name, version))

    resp = make_response('', 201)
    return resp


@pages.route('/count', methods=['GET'])
def count():
    """
    Not sure which nuget command uses this...
    """
    logger.debug("Route: /count")
    resp = make_response(str(db.count_packages(session)))
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


@pages.route('/delete', methods=['DELETE'])
@pages.route('/<package>/<version>', methods=['DELETE'])
@pages.route('/api/v2/package/<package>/<version>', methods=['DELETE'])
def delete(package=None, version=None):
    """
    Used by `nuget delete`.
    """
    logger.debug("Route: /delete")
    if not core.require_auth(request.headers):
        return "api_error: Missing or Invalid API key", 401      # TODO

    if package is not None:
        pkg_name = package
    else:
        pkg_name = request.args.get('id')

    if version is None:
        version = request.args.get('version')
    path = core.get_package_path(pkg_name, version)
    path = Path(current_app.config['SERVER_PATH']) / current_app.config['PACKAGE_DIR'] / path

    if path.exists():
        path.unlink()

    try:
        db.delete_version(session, pkg_name, version)
    except NoResultFound:
        msg = "Version '{}' of Package '{}' was not found."
        return msg.format(pkg_name, version), 404

    logger.info("Sucessfully deleted package %s version %s." % (pkg_name, version))

    return '', 204


@pages.route('/download/<pkg_id>/<version>', methods=['GET'])
def download(pkg_id=None, version=None):
    """
    Indirectly used by `nuget install`.
    """
    logger.debug("Route: /download")

    if pkg_id is None:
        pkg_id = request.args.get('Id')
    if version is None:
        version = request.args.get('Version')

    pkg_name = db.find_pkg_by_id(session, pkg_id).name

    path = core.get_package_path(pkg_name, version)

    # Make sure we're trying to download from our package direcory
    path = Path(current_app.config['SERVER_PATH']) / current_app.config['PACKAGE_DIR'] / path
    abs_path = Path.cwd() / path

    logger.debug("Path to package: %s" % abs_path)
    db.increment_download_count(session, pkg_name, version)
    filename = "{}.{}.nupkg".format(pkg_name, version)
    logger.debug("File name: %s" % filename)

    logger.debug("sending file")
    result = send_file(str(abs_path),
                       mimetype="application/zip",
                       as_attachment=True,
                       attachment_filename=filename)

    header_str = str(result.headers).replace("\r\n", "\r\n  ").strip()
    logger.debug("Header: \n  {}".format(header_str))
    return result, 200


@pages.route('/FindPackagesById()', methods=['GET'])
@pages.route('/Packages(<func_args>)', methods=['GET'])
def find_by_id(func_args=None):
    """
    Used by `nuget install`.

    It looks like the NuGet client expects this to send back a list of all
    versions for the package, and then the client handles extraction of
    an individual version.

    Note that this is different from the newer API
        /Packages(Id='pkg_name',Version='0.1.3')
    which appears to move the version selection to server-side.
    """
    logger.debug("Route: /find_by_id")
    logger.debug("  args: {}".format(request.args))
    logger.debug("  header: {}".format(request.headers))

    if func_args is not None:
        # Using the newer API
        logger.debug(func_args)
        # Parse the args. From what I can tell, the only things sent here are:
        #   'Id': the name of the package
        #   'Version': the version string.
        # Looks like:
        #   "Id='NuGetTest',Version='0.0.2'"
        # Naive implementation
        regex = re.compile(r"^Id='(?P<name>.+)',Version='(?P<version>.+)'$")
        match = regex.search(func_args)
        if match is None:
            msg = "Unable to parse the arg string `{}`!"
            logger.error(msg.format(func_args))
            return msg.format(func_args), 500

        pkg_name = match.group('name')
        version = match.group('version')
        logger.debug("{}, {}".format(pkg_name, version))
    else:
        # old API
        pkg_name = request.args.get('id')
        sem_ver_level = request.args.get('semVerLevel', default=None)
        version = None

    # Some terms are quoted
    pkg_name = pkg_name.strip("'")

    results = db.find_by_pkg_name(session, pkg_name, version)
    logger.debug(results)
    feed = FeedWriter('FindPackagesById', request.url_root)
    resp = make_response(feed.write_to_output(results))
    resp.headers['Content-Type']

    logger.debug(resp.data.decode('utf-8').replace('><',' >\n<'))

    return resp


@pages.route('/Search()', methods=['GET'])
def search():
    """
    Used by `nuget list`.
    """
    logger.debug("Route: /search")
    logger.debug(request.args)
    # TODO: Cleanup this and db.search_pacakges call sig.
    include_prerelease = request.args.get('includePrerelease', default=False)
    order_by = request.args.get('$orderBy', default='Id')
    filter_ = request.args.get('$filter', default=None)
    top = request.args.get('$top', default=30)
    skip = request.args.get('$skip', default=0)
    sem_ver_level = request.args.get('semVerLevel', default='2.0.0')
    search_query = request.args.get('searchTerm', default=None)
    target_framework = request.args.get('targetFramework', default='')

    # Some of the terms have quotes surrounding them
    search_query = search_query.strip("'")
    target_framework = target_framework.strip("'")

    results = db.search_packages(session,
                                 include_prerelease=include_prerelease,
                                 #order_by=order_by,
                                 filter_=filter_,
                                 search_query=search_query,
                                 )

    feed = FeedWriter('Search', request.url_root)
    resp = make_response(feed.write_to_output(results))
    logger.debug("Finished FeedWriter.write_to_output")
    resp.headers['Content-Type'] = FEED_CONTENT_TYPE_HEADER

    # Keep this line for future debugging. Will fill up the logs *very*
    # quickly if there are a lot of packages on the server.
    # logger.debug(resp.data.decode('utf-8').replace('><',' >\n<'))

    return resp


@pages.route('/updates', methods=['GET'])
def updates():
    """
    I thought this was `nuget restore` but that looks to be
    `GET http://localhost:5000/Packages(Id='xunit',Version='2.3.1')`
    """
    logger.debug("Route: /updates")
    ids = request.args.get('packageids').strip("'").split('|')
    versions = request.args.get('versions').strip("'").split('|')
    include_prerelease = request.args.get('includeprerelease', default=False)
    pkg_to_vers = {k: v for k, v in zip(ids, versions)}

    results = db.package_updates(session, pkg_to_vers, include_prerelease)

    feed = FeedWriter('GetUpdates', request.url_root)
    resp = make_response(feed.write_to_output(results))
    resp.headers['Content-Type'] = FEED_CONTENT_TYPE_HEADER
    return resp
