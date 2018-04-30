# -*- coding: utf-8 -*-
"""
"""
import os
import shutil
from io import BytesIO

import pytest

from pynuget import app
from pynuget import routes
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


@pytest.fixture
def put_header():
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


def test_push_no_auth(client, put_header):
    put_header.pop('X-Nuget-ApiKey')
    rv = client.put(
        '/api/v2/package/',
        headers=put_header,
        follow_redirects=True,
    )
    assert rv.status_code == 401


def test_push_invalid_auth(client, put_header):
    app.config['API_KEYS'] = ""
    rv = client.put(
        '/api/v2/package/',
        headers=put_header,
        follow_redirects=True,
    )
    assert rv.status_code == 401


def test_push_no_file(client, put_header):
    rv = client.put(
        '/api/v2/package/',
        headers=put_header,
        follow_redirects=True,
    )
    assert rv.status_code == 409


def test_push_invalid_file(client, put_header):
    data = {'package': (BytesIO(b'Dummy'), 'filename.nupkg')}
    rv = client.put(
        '/api/v2/package/',
        headers=put_header,
        follow_redirects=True,
        data=data,
    )
    assert rv.status_code == 400


def test_push_no_nuspec(client, put_header):
    nupkg_file = os.path.join(DATA_DIR, 'no_nuspec.nupkg')
    with open(nupkg_file, 'rb') as openf:
        data = {'package': (openf, 'filename.nupkg')}
        rv = client.put(
            '/api/v2/package/',
            headers=put_header,
            follow_redirects=True,
            data=data,
        )
        assert rv.status_code == 400


def test_push_multiple_nuspec(client, put_header):
    nupkg_file = os.path.join(DATA_DIR, 'multiple_nuspec.nupkg')
    with open(nupkg_file, 'rb') as openf:
        data = {'package': (openf, 'filename.nupkg')}
        rv = client.put(
            '/api/v2/package/',
            headers=put_header,
            follow_redirects=True,
            data=data,
        )
        assert rv.status_code == 400


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
