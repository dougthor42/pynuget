# -*- coding: utf-8 -*-
"""
"""

import datetime as dt

import pytest
from lxml import etree as et

from pynuget import feedwriter as fw


def test_write(feedwriter, version_row):
    result = feedwriter.write(None)
    assert isinstance(result, bytes)


def test_write_to_output(feedwriter, version_row):
    try:
        feedwriter.write_to_output([version_row])
    except Exception as ex:
        pytest.fail("Unexpected Error: {}".format(ex))


def test_begin_feed(feedwriter):
    feedwriter.begin_feed()
    result = et.tostring(feedwriter.feed)
    assert isinstance(result, bytes)
    print(result)
    assert b'xmlns="http://www.w3.org/2005/Atom"' in result
    assert b'xml:base="https://www.nuget.org/api/v2/"' in result
    assert b'http://schemas.microsoft.com/ado/2007/08/dataservices' in result
    assert b'microsoft.com/ado/2007/08/dataservices/metadata' in result


@pytest.mark.xfail
def test_add_entry(feedwriter, version_row, version_row_xml):
    feedwriter.begin_feed()
    feedwriter.add_entry(version_row)

    expected = version_row_xml
    result = et.tostring(feedwriter.feed)
    assert result == expected


@pytest.mark.xfail
def test_add_entry_meta(feedwriter, version_row, version_row_xml):
    node = et.Element('root')
    feedwriter.add_entry_meta(node, version_row)

    expected = version_row_xml
    result = et.tostring(node)
    assert result == expected


def test_render_meta_date(feedwriter):
    date = dt.datetime(1970, 1, 1, 0, 0, 0, 0)
    result = feedwriter.render_meta_date(date)
    assert result == {'value': "1970-01-01T00:00:00Z", 'type': "Edm.DateTime"}


def test_render_meta_boolean(feedwriter):
    result = feedwriter.render_meta_boolean(False)
    assert result == {'value': 'False', 'type': 'Edm.Boolean'}
    result = feedwriter.render_meta_boolean(True)
    assert result == {'value': 'True', 'type': 'Edm.Boolean'}


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


def test_render_dependencies_xml(feedwriter):
    raw = """
        [
            {"version": "4.0.0", "framework": null, "id": "NLog"},
            {"version": "4.0.0", "framework": "A", "id": "pkg2"},
            {"version": "4.0.0", "framework": "A", "id": "pkg1"},
            {"version": "4.0.0", "framework": "B", "id": "pkg3"},
            {"version": "1.2.0", "id": "pkg4"}
        ]
        """

    result = feedwriter.render_dependencies_xml(raw)
    print(et.tostring(result))
    assert isinstance(result, et._Element)


def test_group_dependencies():
    raw = """
        [
            {"version": "4.0.0", "framework": null, "id": "NLog"},
            {"version": "4.0.0", "framework": "A", "id": "pkg2"},
            {"version": "4.0.0", "framework": "A", "id": "pkg1"},
            {"version": "4.0.0", "framework": "B", "id": "pkg3"},
            {"version": "1.2.0", "id": "pkg4"}
        ]
        """
    import json
    data = json.loads(raw)

    # if no frameworks are listed, they should all be grouped under "None"
    assert fw.group_dependencies([data[4]]) == {None: [data[4]]}

    actual = fw.group_dependencies(data)
    expected = {
        None: [{"version": "4.0.0", "framework": None, "id": "NLog"},
               {"version": "1.2.0", "id": "pkg4"}],
        "A": [{"version": "4.0.0", "framework": "A", "id": "pkg2"},
              {"version": "4.0.0", "framework": "A", "id": "pkg1"}],
        "B": [{"version": "4.0.0", "framework": "B", "id": "pkg3"}],
    }

    assert isinstance(actual, dict)
    assert actual == expected


def test_format_target_framework(feedwriter):
    assert feedwriter.format_target_framework('DNX4.5.1') == 'dnx451'


def test_add_with_attributes(feedwriter):
    node = et.Element('root')
    name = "SomeName"
    value = "SomeValue"
    attributes = {'a': 5, 'b': "foo"}

    expected = b'<root><SomeName a="5" b="foo">SomeValue</SomeName></root>'
    feedwriter.add_with_attributes(node, name, value, attributes)
    assert et.tostring(node) == expected


def test_add_meta(feedwriter):
    node = et.Element('root')
    name = "SomeName"
    value = "SomeValue"
    type_ = 'Edm.Int32'

    # I think this is what we're expecting...
    expected_1 = (
        b'<root>'
        b'<d:SomeName'
        b' xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"'
        b' xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"'
        b' xmlns="http://www.w3.org/2005/Atom"'
        b' type="Edm.Int32">SomeValue</d:SomeName>'
        b'</root>'
    )

    # add_meta doesn't return anything, but modifies `node`.
    feedwriter.add_meta(node, name, value, type_)
    assert et.tostring(node) == expected_1

    # Create a new node
    node = et.Element('root')
    value = None
    expected_2 = (
        b'<root>'
        b'<d:SomeName'
        b' xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"'
        b' xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"'
        b' xmlns="http://www.w3.org/2005/Atom"'
        b' type="Edm.Int32"'
        b' null="true"/>'
        b'</root>'
    )
    feedwriter.add_meta(node, name, value, type_)
    assert et.tostring(node) == expected_2
