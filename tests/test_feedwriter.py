# -*- coding: utf-8 -*-
"""
"""

import datetime as dt
import json
import xml.etree.ElementTree as et

import pytest

from pynuget import feedwriter as fw
from pynuget import db


@pytest.fixture
def feedwriter():
    return fw.FeedWriter(1)


@pytest.fixture
def version_row():
    row = db.Version(
        version_id=1,
        package_id=1,
        version="0.0.1",
        copyright_="No copyright",
        created=dt.datetime(1970, 1, 1, 0, 0, 0, 0),
        dependencies='[{"id": 1, "version": "0.2.3"}]',
        description="Some description",
        icon_url="no url",
        is_prerelease=False,
        package_hash="abc123",
        package_hash_algorithm="Michael Jackson",
        package_size=1024,
        project_url="https://github.com/dougthor42/pynuget/",
        release_notes="No release notes. Sorry!",
        require_license_acceptance=False,
        tags="no tags",
        title="DummyPackage",
        version_download_count=9,
        license_url="https://github.com/dougthor42/pynuget/blob/master/LICENSE",
    )

    pkg = db.Package(package_id=1,
                     title="DummyPackage",
                     download_count=12,
                     latest_version="0.0.1")

    row.package = pkg

    return row


@pytest.fixture
def version_row_xml():
    """The values in here are intimately linked to those in version_row."""
    # I think it's supposed to look like this...
    # Note implicit string concatenation.
    expected = (
        '<root><properties><MinClientVersion />'
        '<Dependencies>1:0.2.3:</Dependencies>'
        '<VersionDownloadCount m:type="int">9</VersionDownloadCount>'
        '<ReleaseNotes>No release notes. Sorry!</ReleaseNotes>'
        '<version>0.0.1</version>'
        '<LicenseUrl>"'
        'https://github.com/dougthor42/pynuget/blob/master/LICENSE"'
        '</LicenseUrl>'
        '<Tags>no tags</Tags><Language m:null="true" />'
        '<ProjectUrl>https://github.com/dougthor42/pynuget/</ProjectUrl>'
        '<IconUrl>no url</IconUrl>'
        '<PackageHashAlgorithm>Michael Jackson</PackageHashAlgorithm>'
        '<PackageHash>abc123</PackageHash>'
        '<Title>DummyPackage</Title>'
        '<PackageSize m:type="int">1024</PackageSize>'
        '<DownloadCount m:type="int">12</DownloadCount>'
        '<NormalizedVersion>0.0.1</NormalizedVersion>'
        '<Created m:type="dt.datetime">1970-01-01T00:00:00Z</Created>'
        '<Description>Some description</Description>'
        '<LicenseNames /><Summary m:null="true" />'
        '<LastEdited m:null="true" m:type="dt.datetime" />'
        '<IsPrerelease m:type="bool">False</IsPrerelease>'
        '<RequireLicenseAcceptance m:type="bool">False'
        '</RequireLicenseAcceptance>'
        '<Copyright>No copyright</Copyright>'
        '<ReportAbuseUrl />'
        '<IsAbsoluteLatestVersion m:type="bool">True'
        '</IsAbsoluteLatestVersion>'
        '<IsLatestVersion m:type="bool">True</IsLatestVersion>'
        '<Published m:type="dt.datetime">1970-01-01T00:00:00Z</Published>'
        '<GalleryDetailsUrl>TBDdetails/1/0.0.1</GalleryDetailsUrl'
        '><LicenseReportUrl />'
        '</properties>'
        '</root>'
    )
    return expected


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


def test_add_entry(feedwriter, version_row):
    feedwriter.begin_feed()
    feedwriter.add_entry(version_row)
#    print(et.tostring(feedwriter.feed))
#    pytest.fail()


def test_add_entry_meta(feedwriter, version_row):
    node = et.Element('root')
    feedwriter.add_entry_meta(node, version_row)
    print(et.tostring(node))
    assert False


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
    expected_1 = b'<root><SomeName m:type="Edm.Int32">SomeValue</SomeName></root>'

    # add_meta doesn't return anything, but modifies `node`.
    feedwriter.add_meta(node, name, value, type_)
    assert et.tostring(node) == expected_1

    # Create a new node
    node = et.Element('root')
    value = None
    expected_2 = b'<root><SomeName m:null="true" m:type="Edm.Int32" /></root>'
    feedwriter.add_meta(node, name, value, type_)
    assert et.tostring(node) == expected_2
