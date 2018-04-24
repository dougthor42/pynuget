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

class FeedWriter(object):

    def __init__(self, id_):
        self.feed_id = id_
        self.base_url = 'TBD'

    def write(self):
        self.begin_feed()
        for result in results:
            self.add_entry(result)
        return self.feed.as_xml()

    def write_to_output(self, results):
        # TODO: header line
        this.write(results)

    def begin_feed(self):
        self.feed = et.fromstring(BASE)
        self.feed.append('id', self.base_url + self.feed_id)
        self.add_with_attributes(self.feed, 'title', self.feed_id,
                {'type': 'text'})
        self.feed.append('updated', cls.format_date(dt.utcnow()))
        self.add_with_attributes(self.feed, 'link', None,
                {'rel': 'self',
                 'title': self.feed_id,
                 'href': self.feed_id,
                 })

    def add_entry(self, row):
        """
        Parameters
        ----------
        row :
            SQLAlchemy result set object
        """
        entry_id = 'Packages(Id="' + row.package_id + '",Version="' + row.version + '")'
        entry = self.feed.append('entry')
        entry.append('id', 'https://www.nuget.org/api/v2/' + entry_id)
        self.add_with_attributes(entry, 'category', None,
                {'term': 'NuGetGallery.V2FeedPackage',
                 'scheme': 'http://schemas.microsoft.com/ado/2007/08/dataservices/scheme',
                 })
        self.add_with_attributes(entry, 'link', None,
            {'rel': 'edit',
             'title': 'V2FeedPackage',
             'href': entry_id,
             })

        # Yes, this "title" is actually the package ID. Actual title is in
        # the metadata.
        self.add_with_attributes(entry, 'title', row.package_id, {'type': 'text'})
        self.add_with_attributes(entry, 'summary', None, {'type': 'text'})
        entry.append('updated', cls.format_date(row.created))

        authors = entry.append('author')
        authors.append('name', row.authors)

        this.add_with_attributes(entry, 'link', None,
            {'rel': 'edit-media',
             'title': 'V2FeedPackage',
             'href': entry_id + '/$value',
             })
        this.add_with_attributes(entry, 'content', None,
            {'type': 'application/zip',
             'src': this.base_url + 'download/' + row.package_id + '/' + row.version,
             })
        this.add_entry_meta(entry, row)

    def add_entry_meta(self, row):
        """
        Parameters
        ----------
        row :
            SQLAlchemy result set object
        """
        properties = entry.append('properties', None,
                'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata')

        meta = {
            'version': row.version,
            'NormalizedVersion': row.version,
            'Copyright': row.copyright,
            'Created': cls.render_meta_date(row.created),
            'Dependencies': self.render_dependencies(row.dependencies),
            'Description': row.description,  # TODO: htmlspecialchars
            'DownloadCount': {'value': row.download_count, 'type': int},
            'GalleryDetailsUrl': self.base_url + 'details/' + row.package_id + '/' + row.version,
            'IconUrl': row.icon_url,  #TODO: htmlspecialchars
            'IsLatestVersion': cls.render_meta_boolean(row.latest_version == row.version),
            'IsAbsoluteLatestVersion': cls.render_meta_boolean(row.latest_version == row.version),
            'IsPrerelease': cls.render_meta_boolean(row.is_prerelease),
            'Language': None,
            'Published': cls.render_meta_date(row.created),
            'PackageHash': row.package_hash,
            'PackageHashAlgorithm': row.package_hash_algorithm,
            'PackageSize': {'value': row.package_size, 'type': int},
            'ProjectUrl': row.project_url,
            'ReportAbuseUrl': '',
            'ReleaseNotes': row.release_notes,  # TODO: htmlspecialchars
            'RequireLicenseAcceptance': cls.render_meta_boolean(row.require_license_acceptance),
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
                type = None

            self.add_meta(properties, name, value, type_)

    def render_meta_date(self, date):
        return {'value': cls.format_date(date), 'type': dt.datetime}

    def render_meta_boolean(self, value):
        return {'value': value, type: bool}

    def format_date(self):
        #  return dt.isoformat(timespec='seconds')      # Py3.6+
        return dt.isoformat()

    def render_dependencies(self, raw):
        if not raw:
            return ''

        data = json.loads(raw)
        if not data:
            return ''

        output = []

        for dependency in data:
            formatted_dependency = dependency.id + dependency.version
            if dependency.framework:
                formatted_dependency += self.format_target_framework(dependency.framework)
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
        node = entry.add_child(name, value)
        for attr_name, attr_value in attributes.items():
            node.add_attribute(attr_name, attr_value)

    def add_meta(self, entry, name, value, type_=None):
        ado_url = 'http://schemas.microsoft.com/ado/2007/08/dataservices',
        node = entry.add_child(
            name,
            value,
            ado_url,
        )

        if type_:
            node.add_attribute(
                'm:type',
                type_,
                ado_url,
            )

        if value is None:
            node.add_attribute(
                'm:null',
                'true',
                ado_url,
            )
