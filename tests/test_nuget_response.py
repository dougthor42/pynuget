# -*- coding: utf-8 -*-
"""
"""

import pytest

from pynuget import nuget_response as nr


@pytest.mark.temp
class TestNuGetResponse():

    def test_to_json_ServiceIndexResourceResponse(self):
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

    def test_to_json_ServiceIndexResponse(self):
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

    def test_json_SearchResponse(self):

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
            nr.SearchResultResponse(4, 5, versions_b),
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
            ' {"id": 4, "version": 5, "versions":'
            ' [{"@id": "e", "downloads": 150, "version": "f"},'
            ' {"@id": "g", "downloads": 250, "version": "h"}]}],'
            ' "totalHits": 561}'
        )
        assert obj.json == expected
