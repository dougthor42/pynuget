# -*- coding: utf-8 -*-
"""
"""

import pytest

from pynuget import feedwriter as fw


@pytest.fixture
def feedwriter():
    return fw.FeedWriter(1)


def test_feedwriter_write(feedwriter):
    raise NotImplementedError
    result = feedwriter.write()

    assert isinstance(result, str)


def test_write_to_output(feedwriter):
    raise NotImplementedError


def test_begin_feed(feedwriter):
    try:
        feedwriter.begin_feed()
    except Exception as ex:
        pytest.fail("Unexpected Error: {}".format(ex))


def test_add_entry(feedwriter):
    raise NotImplementedError


def test_add_entry_meta(feedwriter):
    raise NotImplementedError


def test_render_meta_date(feedwriter):
    raise NotImplementedError


def test_render_meta_boolean(feedwriter):
    result = feedwriter.render_meta_boolean(False)
    assert result == {'value': False, 'type': bool}
    result = feedwriter.render_meta_boolean(True)
    assert result == {'value': True, 'type': bool}



def test_render_dependencies(feedwriter):
    raise NotImplementedError


def test_format_target_framework(feedwriter):
    assert feedwriter.format_target_framework('DNX4.5.1') == 'dnx451'


def test_add_with_attributes(feedwriter):
    raise NotImplementedError


def test_add_meta(feedwriter):
    raise NotImplementedError
