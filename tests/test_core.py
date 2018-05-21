# -*- coding: utf-8 -*-
"""
"""
import shutil
from unittest.mock import MagicMock
import xml.etree.ElementTree as et

import os
import pytest
from werkzeug.datastructures import FileStorage

from pynuget import core
from pynuget import app

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
NAMESPACE = {'nuspec':
             'http://schemas.microsoft.com/packaging/2012/06/nuspec.xsd'}


@pytest.mark.skip("Not Implemented")
def test_api_error():
    pass


def test_require_auth():
    # Make sure that our default config hasn't changed.
    assert app.config['API_KEYS'] == {"ChangeThisKey"}

    headers = {'X-Nuget-Apikey': 'ChangeThisKey'}
    assert core.require_auth(headers)
    headers = {'X-Nuget-Apikey': 'Invaldid Key'}
    assert not core.require_auth(headers)


@pytest.mark.skip("Not Implemented")
def test_request_method():
    pass


def test_get_pacakge_path():
    assert core.get_package_path(1, '0.0.1') == './packagefiles/1/0.0.1.nupkg'


@pytest.mark.skip("Not Implemented")
def test_url_scheme():
    pass


def test_et_to_str():
    node = MagicMock(spec=et.Element)
    assert core.et_to_str(node) is None
    node = MagicMock(text="Hello")
    assert core.et_to_str(node) == "Hello"


def test_parse_nuspec():
    no_metadata = et.parse(os.path.join(DATA_DIR, "no_metadata.nuspec"))
    with pytest.raises(core.ApiException):
        core.parse_nuspec(no_metadata, NAMESPACE)

    no_id = et.parse(os.path.join(DATA_DIR, "no_id.nuspec"))
    with pytest.raises(core.ApiException):
        core.parse_nuspec(no_id, NAMESPACE)

    no_version = et.parse(os.path.join(DATA_DIR, "no_version.nuspec"))
    with pytest.raises(core.ApiException):
        core.parse_nuspec(no_version, NAMESPACE)

    good = et.parse(os.path.join(DATA_DIR, "good.nuspec"))
    nuspec, pkg_name, version = core.parse_nuspec(good, NAMESPACE)
    assert isinstance(nuspec, et.Element)
    assert pkg_name == 'NuGetTest'
    assert version == '0.0.1'


def test_extract_nuspec():
    no_nuspec = os.path.join(DATA_DIR, "no_nuspec.nupkg")
    with pytest.raises(core.ApiException):
        core.extract_nuspec(no_nuspec)

    multiple_nuspec = os.path.join(DATA_DIR, "multiple_nuspec.nupkg")
    with pytest.raises(core.ApiException):
        core.extract_nuspec(multiple_nuspec)

    good = os.path.join(DATA_DIR, "good.nupkg")
    result = core.extract_nuspec(good)
    assert isinstance(result, et.Element)


def test_hash_and_encode_file():
    # Overwrite our server path
    old_server_path = app.config['SERVER_PATH']
    old_package_dir = app.config['PACKAGE_DIR']
    app.config['SERVER_PATH'] = DATA_DIR
    app.config['PACKAGE_DIR'] = '.'
    pkg_name = 'DummyPackage'
    version = '0.0.1'

    good = os.path.join(DATA_DIR, "good.nupkg")
    with open(good, 'rb') as openf:
        file = FileStorage(openf)

        hash_, filesize = core.hash_and_encode_file(file, pkg_name, version)
    assert isinstance(hash_, str)
    assert isinstance(filesize, int)
    assert filesize == 3255

    # Cleanup
    shutil.rmtree(os.path.join(DATA_DIR, pkg_name), ignore_errors=True)
    app.config['SERVER_PATH'] = old_server_path
    app.config['PACKAGE_DIR'] = old_package_dir


def test_determine_dependencies():
    no_dependencies = et.parse(os.path.join(DATA_DIR, "good.nuspec"))
    metadata = no_dependencies.find('nuspec:metadata', NAMESPACE)
    result = core.determine_dependencies(metadata, NAMESPACE)
    assert len(result) == 0

    dependencies = et.parse(os.path.join(DATA_DIR, "dependencies.nuspec"))
    metadata = dependencies.find('nuspec:metadata', NAMESPACE)
    result = core.determine_dependencies(metadata, NAMESPACE)

    # I can't guarantee that the result is deterministic, so sort it by 'id'
    result = sorted(result, key=lambda k: k['id'])
    expected = [
        {'framework': '.NETStandard2.0', 'id': 'A', 'version': '0.0.1'},
        {'framework': '.NETStandard2.0', 'id': 'B', 'version': '0.0.2'},
        {'framework': '.NETStandard2.0', 'id': 'C', 'version': '0.0.3'},
        {'framework': None, 'id': 'D', 'version': '0.0.4'},
        {'framework': None, 'id': 'E', 'version': '0.0.5'},
    ]
    assert result == expected
