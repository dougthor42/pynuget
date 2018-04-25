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
