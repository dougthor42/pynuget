# -*- coding: utf-8 -*-
"""
"""
import os

import pytest

from pynuget import app
from pynuget import routes
from pynuget import commands


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture
def client():
    # override the default paths
    old_server_path = app.config['SERVER_PATH']
    old_package_dir = app.config['PACKAGE_DIR']
    app.config['SERVER_PATH'] = DATA_DIR
    app.config['PACKAGE_DIR'] = '.'
    commands._create_directories(app.config['SERVER_PATH'],
                                 app.config['PACKAGE_DIR'])
    commands._create_db(app.config['DB_BACKEND'],
                        app.config['DB_NAME'],
                        app.config['SERVER_PATH'])

    client = app.test_client()
    yield client
    app.config['SERVER_PATH'] = old_server_path
    app.config['PACKAGE_DIR'] = old_package_dir


def test_root_get(client):
    rv = client.get('/web')
    assert b'Hello World!' in rv.data


def test_index_get(client):
    rv = client.get('/')
    expected = b"<?xml version='1.0' encoding='utf-8' standalone='yes'?>"
    assert rv.data == expected
    assert rv.headers['Content-Type'] == 'text/plain; charset=utf-8'


def test_index_post(client):
    pass


def test_push():
    pass


def test_count(client):
    rv = client.get('/count')
    assert rv.data == b'0'
    assert rv.headers['Content-Type'] == 'text/plain; charset=utf-8'


def test_delete(client):
    pass


def test_download(client):
    pass


def test_find_by_id(client):
    pass


def test_search(client):
    pass


def test_updates(client):
    pass
