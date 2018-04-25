# -*- coding: utf-8 -*-
"""
"""

import pytest

from pynuget import core
from pynuget import app


@pytest.mark.skip("Not Implemented")
def test_api_error():
    pass


def test_require_auth():
    assert app.config['API_KEYS'] == {"ChangeThisKey"}
    assert core.require_auth('ChangeThisKey')
    assert not core.require_auth("Invalid Key")


@pytest.mark.skip("Not Implemented")
def test_request_method():
    pass


def test_get_pacakge_path():
    assert core.get_package_path(1, '0.0.1') == './packagefiles/1/0.0.1.nupkg'


@pytest.mark.skip("Not Implemented")
def test_url_scheme():
    pass
