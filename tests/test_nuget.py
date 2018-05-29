# -*- coding: utf-8 -*-
"""
"""
import os
import shutil

import pytest

from pynuget import core
from pynuget import app
from pynuget import commands

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture
def client():
    # override the default variables.
    # TODO: Move this to just a different config file.
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



@pytest.mark.integration
def test_nuget_list():
    pass


@pytest.mark.integration
def test_nuget_add():
    pass


@pytest.mark.integration
def test_nuget_delete():
    pass


@pytest.mark.integration
def test_nuget_install():
    pass
