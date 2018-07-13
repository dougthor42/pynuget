# -*- coding: utf-8 -*-
"""
"""
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime as dt
from pathlib import Path

from sqlalchemy import create_engine

from pynuget import db
from pynuget import _logging


logger = _logging.setup_logging(True, False, "./pynuget-cli.log")


def init(server_path, package_dir, db_name, db_backend, apache_config,
         replace_wsgi=False, replace_apache=False):
    """
    Initialize the PyNuGet server.

    Parameters
    ----------
    server_path : str
        The directory that you want the server to live in. Must be an
        absolue path. Defaults to /var/www/pynuget
    package_dir : str
        The directory that the packages will be saved in and served from. If
        this value is not an absolute path, `server_path` will be used as
        the root. Defaults to 'packages' in `server_path`
    db_name : str
        The name of the database to use. If db_backend == 'sqlite', then
        this is the relative or absolute path to the SQLite file to use. If
        db_backend != 'sqlite', then this is the name of the Schema to create.
        Defaults to 'packages.db' in `server_path`.
    db_backend : str
        One of ('sqlite', 'mysql', 'postgresql'). Defaults to 'sqlite'.
    apache_config : str
        The name of the apache configuration file. Defaults to 'pynuget.conf'.

    Details
    -------
    +  Create /var/www/pynuget if it doesn't exist.
    +  Create /var/www/pynuget/package_files if it doesn't exist
    +  Create /var/www/pynuget/wsgi.py if it doesn't exist
    +  Copy Apache config if it doesn't exist
    +  Enable Apache site.
    +  Create the DB file or schema if it doesn't exist.
    """
    args = dict(locals())
    _check_permissions()
    _create_directories(server_path, package_dir)
    _create_log_dir("/var/log/pynuget")
    _create_db(db_backend, db_name, server_path)

    _copy_wsgi(server_path, replace_wsgi)

    conf = _copy_apache_config(apache_config, replace_apache)
    _enable_apache_conf(conf.resolve())

    default_config_file = Path(__file__).parent / "default_config.py"
    _save_config(default_config_file, **args)

    _reload_apache()


def clear(server_path, force=False):
    """
    +  Truncate/drop all tables and recreate them
    +  Delete all packages in package_files
    """
    # Confirm:
    ans = input("Are you sure you want to delete all packages? [yN]")
    if ans.lower() in ('y', 'yes'):
        pass
    elif ans.lower() in('n', 'no'):
        logger.debug("User aborted.")
        sys.exit(0)
    else:
        logger.debug("Unknown response '%s'. Aborting." % ans)
        sys.exit(1)

    # Read the config file to find our other locations
    # TODO: I hate this...
    sys.path.append(server_path)
    import config

    # Delete all the packages
    pkg_path = Path(config.SERVER_PATH) / Path(config.PACKAGE_DIR)
    try:
        shutil.rmtree(str(pkg_path))
    except FileNotFoundError:
        logger.warn("Path '%s' does not exist." % str(pkg_path))

    # Delete/drop the database
    if config.DB_BACKEND == 'sqlite':
        sqlite_path = Path(config.SERVER_PATH) / Path(config.DB_NAME)
        try:
            sqlite_path.unlink()
        except FileNotFoundError:
            logger.warn("Path '%s' does not exist." % str(pkg_path))

    # And receate the directories and database based on the config file.
    logger.info("Recreating database and package dir.")
    _create_directories(server_path, config.PACKAGE_DIR)
    _create_db(config.DB_BACKEND, config.DB_NAME, server_path)


def rebuild():
    """Rebuild the package database."""
    raise NotImplementedError
    import config
    # First let's get a list of all the packages in the database.
    # TODO: create the session.
    logger.debug("Getting database packages and versions.")
    db_data = db.search_packages(session, include_prerelease=True)
    db_data = _db_data_to_dict(db_data)

    # Then we'll get the list of all the packages in the package directory
    # Same data structure as the db data.
    pkg_path = Path(config.SERVER_PATH) / Path(config.PACKAGE_DIR)
    file_data = _get_packages_from_files(pkg_path)

    _add_packages_to_db(file_data)
    _remove_packages_from_db(file_data, db_data)


def _create_dir(path):
    """
    Create (and chown) a given directory.

    Parameters
    ----------
    path : pathlib.Path

    Returns
    -------
    None
    """
    path = str(path)
    logger.debug("Creating '%s'" % path)
    try:
        # Note: os.makedirs will not change permissions of existing dirs
        os.makedirs(path,
                    mode=0x2775,        # u=rwx,g=srwx,o=rx
                    exist_ok=True)
        shutil.chown(path, 'www-data', 'www-data')
    except PermissionError:
        logger.warn("Unable to make dir or change owner of %s" % path)


def _replace_prompt(path):
    """Return True if the user wants to replace the file."""
    while True:
        result = input("{} already exists. Replace? [yN] ".format(path))
        result = result.lower()
        if result in ('y', 'yes'):
            return True
        elif result in ('n', 'no', ''):
            return False
        else:
            print("Invalid answer. Please answer 'yes' or 'no'.")


def _now_str():
    """Return the current local time as a str for appending to a filename."""
    return dt.now().strftime("%y%m%d-%H%M%S")


def _copy_file_with_replace_prompt(src, dst, replace=None):
    """
    Copy a file, prompting to replace if it exists. Always save old file.

    Parameters
    ----------
    src : :class:`pathlib.Path`
        The source file to copy.
    dst : :class:`pathlib.Path`
        The location to copy to.
    replace : bool or None

    Returns
    -------
    modified : bool
        If True, the file was modified (created or replaced). If False, the
        existing file was not modified.
    """
    if replace is None:
        replace = _replace_prompt(dst)

    # Save the old file by renaming it with a timestamp.
    # TODO: I don't like this logic very much. There's got to be a better way.
    if dst.exists():
        logger.debug("Path {} already exists".format(dst))
        if replace:
            logger.debug("Replacing (and saving previous version)")
            dst.rename(Path(str(dst) + "." + _now_str()))
            shutil.copy(str(src.resolve()), str(dst))
            return True
        else:
            logger.debug("Not replacing")
            return False
    else:
        logger.debug("Copying new file to {}".format(dst))
        shutil.copy(str(src.resolve()), str(dst))
        return True


def _db_data_to_dict(db_data):
    """
    Convert the result of db.search_packages into a dict of
        {'pkg': ['vers1', 'vers2', ...]}
    """
    data = {}
    for row in db_data:
        try:
            data[row.package.name]
        except KeyError:
            data[row.package.name] = []
        data[row.package.name].append(row.version)

    logger.debug("Found %d database packages." % len(data))
    logger.debug("Found %d database versions." % sum(len(v) for v
                                                     in data.values()))
    return data


def _get_packages_from_files(pkg_path):
    """
    Get a list of packages from the package directory.

    Parameters
    ----------
    pkg_path : :class:`pathlib.Path` or str
        The path to the package directory.

    Returns
    -------
    data : dict
        Dict of {'pkg_name': ['vers1', 'vers2', ...], ...}
    """
    logger.debug("Getting list of packages in package dir.")
    if not isinstance(pkg_path, Path):
        pkg_path = Path(pkg_path)

    data = {}
    # XXX: There's got to be a better way!
    for root, dirs, _ in os.walk(str(pkg_path)):
        rel_path = Path(root).relative_to(pkg_path)
        pkg = str(rel_path.parent)
        if pkg != '.':
            try:
                data[pkg]
            except KeyError:
                data[pkg] = []
            data[pkg].append(rel_path.name)

    logger.debug("Found %d packages." % len(data))
    logger.debug("Found %d versions." % sum(len(v) for v in data.values()))

    return data


def _add_packages_to_db(file_data):
    logger.debug("Adding packages to database.")
    raise NotImplementedError
    for pkg, versions in file_data.items():
        # TODO
        # Check that the package exists in the database.
        if not package_in_db(pkg):
            db.insert_or_update_package(session, None, pkg, versions[0])

        for version in versions:
            if not version_in_db(pkg, version):
                db.insert_version(session, package_id=None, title=pkg,
                                  version=version)


def _remove_packages_from_db(file_data, db_data):
    logger.debug("Removing packages from database.")
    raise NotImplementedError
    for pkg, versions in db_data.items():
        if pkg not in file_data.keys():
            db.delete_version(pkg)
        else:
            for version in versions:
                if version not in file_data[pkg]:
                    db.delete_version(pkg, version)


def _check_permissions():
    """Raise PermissionError if we're not root/sudo."""
    if os.getuid() != 0:
        logger.warn("This script probably needs `sudo`. Trying anyway.")


def _create_directories(server_path, package_dir):
    """Create the server directories if they don't exist."""
    logger.info("Creating directories (if they don't exist).")
    server_path = Path(server_path)
    package_dir = Path(package_dir)

    if not server_path.is_absolute():
        server_path = Path.cwd() / server_path
        logger.warn("'server_path' is not absolute, setting to %s" % server_path)

    if not package_dir.is_absolute():
        package_dir = server_path / package_dir
        logger.warn("'package_dir' is not absolue, setting to %s" % package_dir)

    # os.makedirs will not change permissions of existing directories
    logger.debug("Creating '%s'" % server_path)
    os.makedirs(str(server_path),
                mode=0o2775,        # u=rwx,g=srwx,o=rx
                exist_ok=True)
    shutil.chown(str(server_path), 'www-data', 'www-data')

    logger.debug("Creating '%s'" % package_dir)
    os.makedirs(str(package_dir), mode=0o2775, exist_ok=True)
    shutil.chown(str(package_dir), 'www-data', 'www-data')


def _create_log_dir(log_dir):
    """Create the log directory."""
    logger.info("Creating log directory %s" % log_dir)
    log_path = Path(log_dir)

    if not log_path.is_absolute():
        log_path = Path.cwd() / log_dir
        logger.warn("'log_dir' is not absolute, setting to %s" % log_path)

    logger.debug("Creating '%s'" % log_path)

    try:
        os.makedirs(str(log_path),
                    mode=0x2775,
                    exist_ok=True)
        shutil.chown(str(log_dir), 'www-data', 'www-data')
    except PermissionError:
        logger.warn("Unable to make dir or change owner of %s" % log_dir)


def _create_db(db_backend, db_name, server_path):
    """Create the database (file or schema) if it doesn't exist."""
    logger.info("Creating database.")
    logger.debug("db_backend={}, db_name={}".format(db_backend, db_name))

    url = None

    if db_backend == 'sqlite':
        db_name = Path(server_path) / Path(db_name)
        url = "sqlite:///{}".format(str(db_name))
        logger.debug(url)

        if db_name.exists():
            # assume that the sqlite file has the correct structure.
            pass
        else:
            # create the sqlite file and database.
            engine = create_engine(url, echo=False)
            db.Base.metadata.create_all(engine)
#            shutil.chown(str(db_name), 'www-data', 'www-data')
            os.chmod(str(db_name), 0o0664)
    elif db_backend in ('mysql', 'postgresql'):
        msg = "The backend '%s' is not yet implmented" % db_backend
        logger.error('Other database backends are not yet supported')
        raise NotImplementedError(msg)
    else:
        msg = "Invalid `db_backend` value: %s. Must be one of %s."
        msg = msg % (db_backend, ('sqlite', 'mysql', 'postgresql'))
        logger.error(msg)
        raise ValueError(msg)


def _copy_wsgi(server_path, replace_existing=None):
    """
    Copy the WSGI file to the server directory.

    Parameters
    ----------
    server_path : str
    replace_existing : bool or None
        If None, prompt the user to replace. If True, rename the old file
        and make a new one. If False, do nothing.

    Returns
    -------
    None
    """
    logger.info("Copying WSGI file.")
    original = Path(sys.prefix) / 'data' / 'wsgi.py'
    wsgi_path = Path(server_path) / 'wsgi.py'

    _copy_file_with_replace_prompt(original, wsgi_path, replace_existing)


def _copy_apache_config(apache_config, replace_existing=None):
    """
    Copy the example apache config to the Apache sites.

    Parameters
    ----------
    apache_config : str
        Name of the apache config file. Must not be an absolute path.
    replace : bool or None
        If None, prompt the user to replace the config file. If the config
        file is overwritten (True or user responds True, the old file will
        still be saved). If False, the default config is not copied.

    Returns
    -------
    apache_conf : :class:`pathlib.Path`
        Full path to the apache config file.
    """
    logger.info("Copying example Apache Config.")
    apache_path = Path('/etc/apache2/sites-available/')
    apache_config = Path(apache_config)
    if apache_config.is_absolute():
        raise OSError("'apache_config' must not be an absolue path")
    apache_conf = apache_path / apache_config
    example_conf = Path(sys.prefix) / 'data' / 'apache-example.conf'

    _copy_file_with_replace_prompt(example_conf, apache_conf, replace_existing)

    return apache_conf


def _enable_apache_conf(conf):
    """
    Enable the apache site.

    Enabling a site simply consists of symlinking to the sites-available
    directory.

    Parameters
    ----------
    conf : :class:`pathlib.Path`
        The full path to the apache config file.

    Returns
    -------
    link : :class:`pathlib.Path`
        The path to the symlink.
    """
    logger.info("Enabling Apache site: {}".format(conf))

    link = conf.parent.parent / 'sites-enabled' / conf.name

    try:
        link.symlink_to(conf)
    except FileExistsError:
        logger.info("Site is already enabled.")

    return link


def _reload_apache():
    """Reload the apache configuration."""
    logger.info("Reloading Apache configuration")
    try:
        args = ['service', 'apache2', 'restart']
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as err:
        msg = ("Unlable to reload the apache configuration. Please attempt to"
               " reload it manually.")
        logger.error(err)
        logger.error(msg)


def _save_config(default_config_file, **kwargs):
    """Save the values to the configuration file."""
    logger.info("Saving configuration.")

    # Open the default config file.
    with open(str(default_config_file), 'r') as openf:
        raw = openf.read()

        for variable, new_value in kwargs.items():
            global_variable = variable.upper()

            pat = r'''^(?P<variable>{} = )['"](?P<value>.+)['"]$'''
            pat = re.compile(pat.format(global_variable), re.MULTILINE)

            old_value = pat.search(raw)
            if old_value is None:
                logger.debug("ignoring {}".format(global_variable))
                continue

            old_value = old_value.group('value')
            if old_value == new_value:
                logger.debug("Parameter '{}' unchanged.".format(variable))
                continue

            raw = pat.sub('\g<variable>"{}"'.format(new_value), raw)
            new_value = pat.search(raw).group('value')
            msg = "Replaced %s: '%s' with '%s'"
            logger.debug(msg % (variable, old_value, new_value))

    config_path = Path(kwargs['server_path']) / Path('config.py')
    with open(str(config_path), 'w') as openf:
        openf.write(raw)

    logger.debug("Configuration saved to `%s`" % config_path.as_posix())
