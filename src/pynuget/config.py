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

# Schema name or path to SQLite file.
DB_NAME = ""

# Where nuget packages will be saved to and sourced from.
PACKAGE_DIR = "/var/www/pynuget/packagefiles"

# A list (well, set) of valid API Keys
API_KEYS = {
    "ChangeThisKey",
}

# These are only used for non-SQLite backends like MySQL or PostgreSQL.
DB_USER = None
DB_PASSWORD = None
