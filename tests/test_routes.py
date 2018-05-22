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


@pytest.fixture
def populated_db(client, put_header):
    """Build up a dummy database of NuGet packages."""
    # TODO: make this just DB calls instead of full API
    check_push(201, client, put_header, 'good.nupkg')
    yield client


def check_push(expected_code, client, header, file=None):
    data = None
    if file:
        nupkg_file = os.path.join(DATA_DIR, file)
        openf = open(nupkg_file, 'rb')
        data = {'package': (openf, 'filename.nupkg')}

    rv = client.put(
        '/api/v2/package/',
        headers=header,
        follow_redirects=True,
        data=data,
    )

    try:
        openf.close()
    except Exception:
        pass

    assert rv.status_code == expected_code


def test_root_get(client):
    rv = client.get('/web')
    assert b'Hello World!' in rv.data


def test_index_get(client):
    rv = client.get('/')
    expected = b"<?xml version='1.0' encoding='utf-8' standalone='yes'?>"
    assert rv.data == expected
    assert rv.headers['Content-Type'] == 'text/plain; charset=utf-8'


@pytest.mark.skip("Test not written")
def test_index_post(client):
    pass


def test_push_ok(client, put_header):
    check_push(201, client, put_header, 'good.nupkg')


def test_push_no_auth(client, put_header):
    put_header.pop('X-Nuget-ApiKey')
    check_push(401, client, put_header)


def test_push_invalid_auth(client, put_header):
    app.config['API_KEYS'] = ""
    check_push(401, client, put_header)


def test_push_no_file(client, put_header):
    check_push(409, client, put_header)


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
    check_push(400, client, put_header, 'no_nuspec.nupkg')


def test_push_multiple_nuspec(client, put_header):
    check_push(400, client, put_header, 'multiple_nuspec.nupkg')


def test_push_invalid_pkg_name(client, put_header):
    check_push(400, client, put_header, 'invalid_name.nupkg')


def test_push_invalid_pkg_version(client, put_header):
    check_push(400, client, put_header, 'invalid_version.nupkg')


def test_push_duplicate_pkg_version(client, put_header):
    check_push(201, client, put_header, 'good.nupkg')
    check_push(409, client, put_header, 'good.nupkg')


@pytest.mark.skip("Gotta figure this one out...")
def test_push_fail_to_save_file(client, put_header):
    pass
    #assert rv.status_code == 500


@pytest.mark.skip("Gotta figure this one out...")
def test_push_fail_parse_dependencies(client, put_header):
    pass
    #assert rv.status_code == 400


def test_count(client):
    rv = client.get('/count')
    assert rv.data == b'0'
    assert rv.headers['Content-Type'] == 'text/plain; charset=utf-8'


def test_delete(client, put_header):
    check_push(201, client, put_header, 'good.nupkg')
    rv = client.delete(
        '/api/v2/package/NuGetTest/0.0.1',
        headers=put_header,
        follow_redirects=True,
        data=None,
    )
    assert rv.status_code == 204


@pytest.mark.skip("Test not written")
def test_download(client):
    pass


@pytest.mark.skip("Test not written")
def test_find_by_id(client):
    pass


def test_search(populated_db):
    client = populated_db

    rv = client.get(
        "/Search()?$orderby=Id&searchTerm='NuGetTest'&targetFramework=''&includePrerelease=true&$skip=0&$top=30&semVerLevel=2.0.0",
        follow_redirects=True,
    )

    assert b"Douglas Thor" in rv.data
    assert b"<d:Id>NuGetTest</d:Id>" in rv.data


def test_search_not_found(populated_db):
    client = populated_db

    rv = client.get(
        "/Search()?$orderby=Id&searchTerm='aaa'&targetFramework=''&includePrerelease=true&$skip=0&$top=30&semVerLevel=2.0.0",
        follow_redirects=True,
    )

    assert b"Douglas Thor" not in rv.data
    assert b"<d:Id>NuGetTest</d:Id>" not in rv.data


@pytest.mark.skip("Test not written")
def test_updates(client):
    pass


@pytest.mark.integration
def test_list(populated_db):
    """ List is just the same as Search with no search term. """
    client = populated_db

    rv = client.get(
        "/Search()?$orderby=Id&searchTerm=''&targetFramework=''&includePrerelease=true&$skip=0&$top=30&semVerLevel=2.0.0",
        follow_redirects=True,
    )

    assert b"Douglas Thor" in rv.data
    assert b"<d:Id>NuGetTest</d:Id>" in rv.data
