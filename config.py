# -*- coding: utf-8 -*-
"""
"""
import os
import sys

# Log file location. Log rotations/archives will be put in LOG_DIR.
LOG_FILE = 'pynuget.log'
LOG_DIR = "/var/log/pynuget"
if sys.platform == 'win32':
    LOG_DIR = 'C:/Logs/pynuget'
LOG_PATH = os.path.normpath(os.path.join(LOG_DIR, LOG_FILE))

# The database backend to use.
# Must be ond of ("sqlite", "mysql", "postgresql")
DB_BACKEND = "sqlite"

# Schema name or path to SQLite file.
DB_NAME = "nuget_packages.sqlite"

# Server path: root path for things like the SQLite file and the packge files.
# Must be asolute.
SERVER_PATH = "/var/www/pynuget"

# Where nuget packages will be saved to and sourced from.
# Can be absolute or relative. Defaults to $SERVER_PATH\$PACAKGE_DIR
PACKAGE_DIR = "nuget_packages"

# The name of the Apache configuration file
APACHE_CONFIG = "pynuget.conf"

# A list (well, set) of valid API Keys
API_KEYS = {
    "ChangeThisKey",
}

# These are only used for non-SQLite backends like MySQL or PostgreSQL.
DB_USER = None
DB_PASSWORD = None
