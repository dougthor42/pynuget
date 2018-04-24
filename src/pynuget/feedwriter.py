# -*- coding: utf-8 -*-
"""
"""

import datetime as dt
import json
import re
import xml.etree.ElementTree as et

BASE = """<?xml version="1.0" encoding="utf-8" ?>
<feed
  xml:base="https://www.nuget.org/api/v2/"
  xmlns="http://www.w3.org/2005/Atom"
  xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
  xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
>
</feed>
"""
ADO_BASE_URL = "http://schemas.microsoft.com/ado/2007/08/dataservices"
ADO_SCHEMA_URL = ADO_BASE_URL + "/scheme"
ADO_METADATA_URL = ADO_BASE_URL + "/metadata"


class FeedWriter(object):

    def __init__(self, id_):
        self.feed_id = id_
        self.base_url = 'TBD'

    def write(self, results):
        self.begin_feed()
        for result in results:
            self.add_entry(result)
        return self.feed.as_xml()

    def write_to_output(self, results):
        # TODO: header line
        self.write(results)

    def begin_feed(self):
        self.feed = et.fromstring(BASE)
        node = et.Element('id', text=(self.base_url + str(self.feed_id)))
        self.feed.append(node)
        self.add_with_attributes(
            self.feed,
            'title',
            self.feed_id,
            {'type': 'text'},
        )
        node = et.Element('updated',
                          text=self.format_date(dt.datetime.utcnow()))
        self.feed.append(node)
        self.add_with_attributes(
            self.feed,
            'link',
            None,
            {'rel': 'self', 'title': self.feed_id, 'href': self.feed_id},
        )

    def add_entry(self, row):
        """
        Parameters
        ----------
        row :
            SQLAlchemy result set object
        """
        entry_id = 'Packages(Id="{}",Version="{}")'.format(row.package_id,
                                                           row.version)
        entry = self.feed.append('entry')
        entry.append('id', 'https://www.nuget.org/api/v2/' + entry_id)
        self.add_with_attributes(
            entry,
            'category',
            None,
            {'term': 'NuGetGallery.V2FeedPackage', 'scheme': ADO_SCHEMA_URL},
        )
        self.add_with_attributes(
            entry,
            'link',
            None,
            {'rel': 'edit', 'title': 'V2FeedPackage', 'href': entry_id},
        )

        # Yes, this "title" is actually the package ID. Actual title is in
        # the metadata.
        self.add_with_attributes(entry, 'title', row.package_id,
                                 {'type': 'text'})
        self.add_with_attributes(entry, 'summary', None, {'type': 'text'})
        entry.append('updated', self.format_date(row.created))

        authors = entry.append('author')
        authors.append('name', row.authors)

        self.add_with_attributes(
            entry,
            'link',
            None,
            {'rel': 'edit-media',
             'title': 'V2FeedPackage',
             'href': entry_id + '/$value',
             },
        )
        url = "{}download/{}/{}".format(self.base_url, row.package_id,
                                        row.version)
        self.add_with_attributes(
            entry,
            'content',
            None,
            {'type': 'application/zip', 'src': url},
        )
        self.add_entry_meta(entry, row)

    def add_entry_meta(self, entry, row):
        """
        Parameters
        ----------
        row :
            SQLAlchemy result set object
        """
        properties = entry.append('properties', None, ADO_METADATA_URL)

        meta = {
            'version': row.version,
            'NormalizedVersion': row.version,
            'Copyright': row.copyright,
            'Created': self.render_meta_date(row.created),
            'Dependencies': self.render_dependencies(row.dependencies),
            'Description': row.description,  # TODO: htmlspecialchars
            'DownloadCount': {'value': row.download_count, 'type': int},
            'GalleryDetailsUrl': self.base_url + 'details/' + row.package_id + '/' + row.version,
            'IconUrl': row.icon_url,  #TODO: htmlspecialchars
            'IsLatestVersion': self.render_meta_boolean(row.latest_version == row.version),
            'IsAbsoluteLatestVersion': self.render_meta_boolean(row.latest_version == row.version),
            'IsPrerelease': self.render_meta_boolean(row.is_prerelease),
            'Language': None,
            'Published': self.render_meta_date(row.created),
            'PackageHash': row.package_hash,
            'PackageHashAlgorithm': row.package_hash_algorithm,
            'PackageSize': {'value': row.package_size, 'type': int},
            'ProjectUrl': row.project_url,
            'ReportAbuseUrl': '',
            'ReleaseNotes': row.release_notes,  # TODO: htmlspecialchars
            'RequireLicenseAcceptance': self.render_meta_boolean(row.require_license_acceptance),
            'Summary': None,
            'Tags': row.tags,
            'Title': row.title,
            'VersionDownloadCount': {'value': row.version_download_count, 'type': int},
            'MinClientVersion': '',
            'LastEdited': {'value': None, 'type': dt.DateTime},
            'LicenseUrl': row.license_url,
            'LicenseNames': '',
            'LicenseReportUrl': '',
        }

        for name, data in meta.items():
            if isinstance(data, dict):
                value = data['value']
                type_ = data['type']
            else:
                value = data
                type_ = None

            self.add_meta(properties, name, value, type_)

    def render_meta_date(self, date):
        return {'value': self.format_date(date) + "Z", 'type': dt.datetime}

    def render_meta_boolean(self, value):
        return {'value': value, 'type': bool}

    def format_date(self, value):
        #  return value.isoformat(timespec='seconds')      # Py3.6+
        return value.isoformat()

    def render_dependencies(self, raw):
        if not raw:
            return ''

        try:
            data = json.loads(raw)
        except json.decoder.JSONDecodeError:
            return ''

        output = []

        for dependency in data:
            formatted_dependency = "{}:{}:".format(dependency['id'],
                                                   dependency['version'])
            if 'framework' in dependency.keys():
                formatted_dependency += self.format_target_framework(
                    dependency['framework'],
                )
            output.append(formatted_dependency)

        return "|".join(output)

    def format_target_framework(self, framework):
        """Format a raw target framework from a NuSpec into the format
        used in the packages feed.

        Eg:
        DNX4.5.1 -> dnx451
        DNXCore5.0 -> dnxcore50
        """
        return re.sub('[^A-Z0-9]', '', framework).lower()

    def add_with_attributes(self, entry, name, value, attributes):
        """

        Parameters
        ----------
        entry :
            Looks to be a SimpleXMLElement node object
        attributes :
            Dict, I think.
        """
        child = et.Element(name)
        child.text = value
        entry.append(child)
        for attr_name, attr_value in attributes.items():
            child.set(attr_name, str(attr_value))

    def add_meta(self, entry, name, value, type_=None):
        child = et.Element(name)
        child.text = value
        entry.append(child)

        if type_:
            child.set('m:type', type_)

        if value is None:
            child.set('m:null', 'true')
