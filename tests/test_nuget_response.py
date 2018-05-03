# -*- coding: utf-8 -*-
"""
"""
import json
import pytest

from pynuget import nuget_response as nr


@pytest.mark.temp
def test__rename_keys():

    # Normal serializable objects should not even call this function, and so
    # and error should be raised.
    obj = {"a": "b"}
    with pytest.raises(AttributeError):
        nr._rename_keys(obj)

    # The function acceptes all items that inherit from Object. If they do
    # not define `json_key_map` at the class level, then they are unchanged.
    class Temp(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b
    obj = Temp("a", 5)
    result = nr._rename_keys(obj)
    assert result == {"a": "a", "b": 5}

    # Any object that defines "json_key_map" should be modified
    class Temp(object):
        json_key_map = {"b": "@type"}
        def __init__(self, a, b):
            self.a = a
            self.b = b
    obj = Temp("a", 5)
    result = nr._rename_keys(obj)
    assert result == {"a": "a", "@type": 5}

    # Items with a value of "None" get removed.
    class Temp(object):
        json_key_map = {"b": "@type"}
        def __init__(self, a, b):
            self.a = a
            self.b = b
    obj = Temp(None, 5)
    result = nr._rename_keys(obj)
    assert result == {"@type": 5}


@pytest.mark.temp
def test__rename_keys_encoder():

    # Nested objects should work too, but only when we run the function
    # via the encoder (since that handles the recursion).
    class Temp(object):
        json_key_map = {"b": "@type"}
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class Parent(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b

    obj = Parent(Temp("a", 5), 10)
    encoded = json.JSONEncoder(sort_keys=True,
                               default=nr._rename_keys).encode(obj)
    result = json.loads(encoded)
    assert result == {"a": {"@type": 5, "a": "a"}, "b": 10}


def test_json_ServiceIndexResourceResponse():
    obj = nr.ServiceIndexResourceResponse(
        url="aaa",
        resource_type="bbb",
    )

    expected = '{"@id": "aaa", "@type": "bbb"}'
    assert obj.json == expected

    obj = nr.ServiceIndexResourceResponse(
        url="ccc",
        resource_type="ddd",
        comment="foo",
    )

    expected = '{"@id": "ccc", "@type": "ddd", "comment": "foo"}'
    assert obj.json == expected


def test_json_ServiceIndexResponse():
    resources = [
        nr.ServiceIndexResourceResponse("a", "b"),
        nr.ServiceIndexResourceResponse("c", "d", "e"),
    ]
    obj = nr.ServiceIndexResponse(
        version="3.0.0",
        resources=resources,
    )

    expected = (
        '{'
        '"resources": ['
        '{"@id": "a", "@type": "b"},'
        ' {"@id": "c", "@type": "d", "comment": "e"}'
        '], "version": "3.0.0"'
        '}'
    )
    assert obj.json == expected


def test_json_SearchResponse():

    versions_a = [
        nr.SearchResultVersionResponse("a", "b", 100),
        nr.SearchResultVersionResponse("c", "d", 50),
    ]
    versions_b = [
        nr.SearchResultVersionResponse("e", "f", 150),
        nr.SearchResultVersionResponse("g", "h", 250),
    ]

    data = [
        nr.SearchResultResponse(1, 2, versions_a),
        nr.SearchResultResponse(4, 5, versions_b, project_url="http://no"),
    ]
    obj = nr.SearchResponse(
        total_hits=561,
        data=data,
    )

    expected = (
        '{"data":'
        ' [{"id": 1, "version": 2, "versions":'
        ' [{"@id": "a", "downloads": 100, "version": "b"},'
        ' {"@id": "c", "downloads": 50, "version": "d"}]},'
        ' {"id": 4, "projectUrl": "http://no", "version": 5, "versions":'
        ' [{"@id": "e", "downloads": 150, "version": "f"},'
        ' {"@id": "g", "downloads": 250, "version": "h"}]}],'
        ' "totalHits": 561}'
    )
    assert obj.json == expected
