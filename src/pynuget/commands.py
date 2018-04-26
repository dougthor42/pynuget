# -*- coding: utf-8 -*-
"""
"""
import os
import shutil
import subprocess
from pathlib import Path

from sqlalchemy import create_engine

from pynuget import db
from pynuget import _logging


logger = _logging.setup_logging(True, False, "./pynuget-cli.log")


def init(server_path, package_dir, db_name, db_backend, apache_config):
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
    _check_permissions()
    _create_directories(server_path, package_dir)
    _create_db(db_backend, db_name)

    # TODO
    _copy_wsgi()

    _copy_apache_config(apache_config)


def clear():
    """
    +  Truncate/drop all tables and recreate them
    +  Delete all packages in package_files
    """
    pass


def _check_permissions():
    """Raise PermissionError if we're not root/sudo."""
    if os.getuid() != 0:
        raise PermissionError("This script must be run using `sudo`. Sorry!")


def _create_directories(server_path, package_dir):
    """Create the server directories if they don't exist."""
    logger.info("Creating directories (if they don't exist).")
    server_path = Path(server_path)
    package_dir = Path(package_dir)

    if not server_path.is_absolute():
        raise OSError("'server_path' must be absolue")

    if not package_dir.is_absolute():
        package_dir = server_path / package_dir
        logger.debug("'package_dir' is not absolue, setting to %s" % package_dir)

    # os.makedirs will not change permissions of existing directories
    logger.debug("Creating '%s'" % server_path)
    os.makedirs(str(server_path),
                mode=0o2775,        # u=rwx,g=srwx,o=rx
                exist_ok=True)

    logger.debug("Creating '%s'" % package_dir)
    os.makedirs(str(package_dir), mode=0o2775, exist_ok=True)
    shutil.chown(str(package_dir), 'www-data', 'www-data')


def _create_db(db_backend, db_name):
    """Create the database (file or schema) if it doesn't exist."""
    logger.info("Creating database.")
    logger.debug("db_backend={}, db_name={}".format(db_backend, db_name))

    url = None

    if db_backend == 'sqlite':
        db_name = Path(db_name)

        if db_name.exists():
            # assume that the sqlite file has the correct structure.
            pass
        else:
            # create the sqlite file and database.
            engine = create_engine(url, echo=False)
            db.Base.metadata.create_all(engine)
            shutil.chown(str(db_name), 'www-data', 'www-data')
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


def _copy_wsgi():
    """Copy the WSGI file to the server directory."""
    logger.info("Copying WSGI file.")
    pass


def _copy_apache_config(apache_config):
    """Copy the example apache config to the Apache sites."""
    logger.info("Copying example Apache Config.")
    apache_path = Path('/etc/apache2/site-available/')
    apache_config = Path(apache_config)
    if apache_config.is_absolute():
        raise OSError("'apache_config' must not be an absolue path")
    apache_config = apache_path / apache_config

    if not apache_config.exists():
        shutil.copy('apache-example.conf', apache_config.resolve())


def _enable_apache_conf(apache_config):
    """Enable the apache site."""
    logger.info("Enabling Apache site.")
    try:
        subprocess.run(['a2ensite', apache_config], shell=True, check=True)
    except subprocess.CalledProcessError as err:
        logger.error("Unable to enable the Apache site '%s'" % apache_config)
        logger.error(err)
