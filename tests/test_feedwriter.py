# -*- coding: utf-8 -*-
"""
"""

import datetime as dt
import json

import pytest

from pynuget import feedwriter as fw


@pytest.fixture
def feedwriter():
    return fw.FeedWriter(1)


@pytest.mark.skip("Not Implemented")
def test_feedwriter_write(feedwriter):
    result = feedwriter.write()

    assert isinstance(result, str)


@pytest.mark.skip("Not Implemented")
def test_write_to_output(feedwriter):
    pass


def test_begin_feed(feedwriter):
    try:
        feedwriter.begin_feed()
    except Exception as ex:
        pytest.fail("Unexpected Error: {}".format(ex))


@pytest.mark.skip("Not Implemented")
def test_add_entry(feedwriter):
    pass


@pytest.mark.skip("Not Implemented")
def test_add_entry_meta(feedwriter):
    pass


def test_render_meta_date(feedwriter):
    date = dt.datetime(1970, 1, 1, 0, 0, 0, 0)
    result = feedwriter.render_meta_date(date)
    assert result == {'value': "1970-01-01T00:00:00Z", 'type': dt.datetime}


def test_render_meta_boolean(feedwriter):
    result = feedwriter.render_meta_boolean(False)
    assert result == {'value': False, 'type': bool}
    result = feedwriter.render_meta_boolean(True)
    assert result == {'value': True, 'type': bool}


def test_render_dependencies(feedwriter):
    raw = """
        [
            {"id": 1, "version": "0.2.3"},
            {"id": 2, "version": "1.2.3"},
            {"id": 3, "version": "2.5.0", "framework": "DNX4.5.1"}
        ]
        """

    # Test when raw is empty or None
    assert feedwriter.render_dependencies('') == ''
    assert feedwriter.render_dependencies(None) == ''

    # Test for invalid JSON
    assert feedwriter.render_dependencies('invalid json}') == ''

    # Test the good stuff
    result = feedwriter.render_dependencies(raw)
    assert isinstance(result, str)
    assert result == "1:0.2.3:|2:1.2.3:|3:2.5.0:dnx451"


def test_format_target_framework(feedwriter):
    assert feedwriter.format_target_framework('DNX4.5.1') == 'dnx451'


@pytest.mark.skip("Not Implemented")
def test_add_with_attributes(feedwriter):
    pass


@pytest.mark.skip("Not Implemented")
def test_add_meta(feedwriter):
    pass
