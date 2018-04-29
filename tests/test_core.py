# -*- coding: utf-8 -*-
"""
"""
from unittest.mock import MagicMock
import xml.etree.ElementTree as et

import pytest

from pynuget import core
from pynuget import app


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
