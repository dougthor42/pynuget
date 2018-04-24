# -*- coding: utf-8 -*-
"""
"""

import pytest

from pynuget import core


def test_api_error():
    pass


def test_require_auth():
    pass


def test_request_method():
    pass


def test_get_pacakge_path():
    assert core.get_package_path(1, '0.0.1') == './packagefiles/1/0.0.1.nupkg'


def test_url_scheme():
    pass
