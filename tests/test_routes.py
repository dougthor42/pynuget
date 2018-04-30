# -*- coding: utf-8 -*-
"""
"""

import pytest

from pynuget import app
from pynuget import routes


@pytest.fixture
def client():

    client = app.test_client()
    yield client


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