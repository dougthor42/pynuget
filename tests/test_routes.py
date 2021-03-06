# -*- coding: utf-8 -*-
"""
"""
import os
from io import BytesIO

import pytest

from . import helpers
from .helpers import check_push
from pynuget import routes


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.mark.parametrize("url", ['/', '/index'])
def test_root_get(client, url):
    rv = client.get(url)
    assert b"This is a NuGet compatible package index" in rv.data
    assert rv.status_code == 200


@pytest.mark.skip("Test not written")
def test_index_post(client):
    pass


@pytest.mark.integration
def test_push_ok(client, put_header):
    check_push(201, client, put_header, 'good.nupkg')


def test_push_no_auth(client, put_header):
    put_header.pop('X-Nuget-ApiKey')
    check_push(401, client, put_header)


def test_push_invalid_auth(client, put_header):
    put_header['X-Nuget-ApiKey'] = "the wrong key"
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


def test_push_invalid_nuspec(client, put_header):
    check_push(400, client, put_header, 'invalid_nuspec.nupkg')


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


def test_metadata(client):
    rv = client.get('/$metadata')
    assert rv.status_code == 200
    assert b'<?xml version="1.0" encoding="utf-8"?>' in rv.data
    assert b'xml:base="http://localhost' in rv.data
    assert b'<workspace>' in rv.data
    assert b'<atom:title type="text">Default</atom:title>' in rv.data
    assert b'<atom:title type="text">Packages</atom:title>' in rv.data
    assert b'</workspace>' in rv.data
    assert b'</service>' in rv.data
    assert 'application/atomsvc+xml;' in rv.headers['Content-Type']
    assert ' charset=utf-8' in rv.headers['Content-Type']
    assert rv.headers['Pragma'] == 'no-cache'
    assert rv.headers['Cache-Control'] == 'no-cache'


def test_count(client):
    rv = client.get('/count')
    assert rv.data == b'0'
    assert rv.headers['Content-Type'] == 'text/plain; charset=utf-8'


@pytest.mark.integration
def test_delete(client, put_header):
    check_push(201, client, put_header, 'good.nupkg')
    rv = client.delete(
        '/api/v2/package/NuGetTest/0.0.1',
        headers=put_header,
        follow_redirects=True,
        data=None,
    )
    assert rv.status_code == 204


def test_delete_no_auth(populated_db, put_header):
    put_header.pop('X-Nuget-ApiKey')
    rv = populated_db.delete(
        '/api/v2/package/NuGetTest/0.0.1',
        headers=put_header,
        follow_redirects=True,
        data=None,
    )
    assert rv.status_code == 401


def test_delete_invalid_auth(populated_db, put_header):
    put_header['X-Nuget-ApiKey'] = "the wrong key"
    rv = populated_db.delete(
        '/api/v2/package/NuGetTest/0.0.1',
        headers=put_header,
        follow_redirects=True,
        data=None,
    )
    assert rv.status_code == 401


def test_delete_package_not_found(populated_db, put_header):
    rv = populated_db.delete(
        '/api/v2/package/aaa/0.0.1',
        headers=put_header,
        follow_redirects=True,
        data=None,
    )
    assert rv.status_code == 404


def test_delete_version_not_found(populated_db, put_header):
    rv = populated_db.delete(
        '/api/v2/package/NuGetTest/9.9.9',
        headers=put_header,
        follow_redirects=True,
        data=None,
    )
    assert rv.status_code == 404


def test_delete_alternate_url(populated_db, put_header):
    rv = populated_db.delete(
        '/delete?id=NuGetTest&version=0.0.1',
        headers=put_header,
        follow_redirects=True,
        data=None,
    )
    assert rv.status_code == 204


def test_download(populated_db):
    client = populated_db

    rv = client.get(
        "download/1/0.0.1",
        follow_redirects=True,
    )

    assert rv.status_code == 200


def test_find_by_id(populated_db):
    client = populated_db

    rv = client.get(
        "/FindPackagesById()?id='NuGetTest'&semVerLevel=2.0.0",
        follow_redirects=True,
    )

    assert b"Douglas Thor" in rv.data
    assert b"<d:Id>NuGetTest</d:Id>" in rv.data


def test_packages(populated_db):
    client = populated_db

    rv = client.get(
        "/Packages(Id='NuGetTest',Version='0.0.1')",
        follow_redirects=True,
    )

    assert b"Douglas Thor" in rv.data
    assert b"<d:Id>NuGetTest</d:Id>" in rv.data


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
