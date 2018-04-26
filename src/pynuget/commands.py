# -*- coding: utf-8 -*-
"""
"""

def init():
    """
    +  Create /var/www/pynuget if it doesn't exist.
    +  Create /var/www/pynuget/package_files if it doesn't exist
    +  Create /var/www/pynuget/wsgi.py if it doesn't exist
    +  Copy Apache config if it doesn't exist
    +  Enable Apache site.
    +  Create the DB file or schema if it doesn't exist.
    +  Restart Apache
    """
    pass


def clear():
    """
    +  Truncate/drop all tables and recreate them
    +  Delete all packages in package_files
    """
    pass