# -*- coding: utf-8 -*-
"""
"""
from unittest.mock import MagicMock
import xml.etree.ElementTree as et

import os
import pytest

from pynuget import core
from pynuget import app

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./data")
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
    nuspec, id_, version = core.parse_nuspec(good, NAMESPACE)
    assert isinstance(nuspec, et.Element)
    assert id_ == 'NuGetTest'
    assert version == '0.0.1'
