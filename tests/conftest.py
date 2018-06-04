# -*- coding: utf-8 -*-
"""
"""
import os
import shutil

import pytest

from pynuget import create_app
from pynuget import commands


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture
def client():
    """
    Create a client app for testing.

    Uses the `commands` module to create the required directories and database
    file so tests can run.

    Removes the items after a test is complete.
    """
    # override the default variables.
    # TODO: Move this to just a different config file.

    app = create_app()

    old_server_path = app.config['SERVER_PATH']
    old_package_dir = app.config['PACKAGE_DIR']
    server_path = app.config['SERVER_PATH'] = os.path.join(DATA_DIR, 'server')
    pkg_dir = app.config['PACKAGE_DIR'] = 'pkgs'
    old_api_keys = app.config['API_KEYS']
    api_keys = app.config['API_KEYS'] = ['no_key']

    commands._create_directories(server_path, pkg_dir)
    commands._create_db(app.config['DB_BACKEND'],
                        app.config['DB_NAME'],
                        server_path)

    client = app.test_client()
    yield client

    # Cleanup
    os.remove(os.path.join(server_path, app.config['DB_NAME']))
    shutil.rmtree(str(server_path), ignore_errors=False)
    app.config['SERVER_PATH'] = old_server_path
    app.config['PACKAGE_DIR'] = old_package_dir
    app.config['API_KEYS'] = old_api_keys


@pytest.fixture
def put_header():
    """
    Creates a header suitable for a "PUT" HTTP method to the server.
    """
    header = {
        'X-Nuget-Client-Version': '4.6.2',
        'X-Nuget-ApiKey': 'no_key',
        'Connection': 'Keep-Alive',
        'User-Agent': 'NuGet Command Line/4.6.2 (Microsoft Windows NT 6.2.9200.0)',
        'Expect': '100-continue',
        'Accept-Language': 'en-US',
        'Content-Type': 'multipart/form-data; boundary="0912807c-e081-4c9f-8228-67484e6023a4"',
        'Host': 'localhost:5000',
        'Accept-Encoding': 'gzip, deflate',
    }
    return header
