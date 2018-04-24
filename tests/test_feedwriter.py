# -*- coding: utf-8 -*-
"""
"""

import pytest

from pynuget import feedwriter as fw


@pytest.fixture
def feedwriter():
    return fw.FeedWriter(1)


def test_feedwriter_write(feedwriter):
    result = feedwriter.write()

    assert isinstance(result, str)
