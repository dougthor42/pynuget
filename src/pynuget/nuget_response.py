# -*- coding: utf-8 -*-
"""
"""

import json

from pynuget import logger
from pynuget.core import PyNuGetException





class NuGetResponse(object):

    @property
    def json(self):
        """Return the object as JSON to send to NuGet"""
        encoder = json.JSONEncoder(sort_keys=True, default=_rename_keys)
        return encoder.encode(self)


class ServiceIndexResponse(NuGetResponse):

    def __init__(self, version, resources):
        """
        version : str
        resources : list of :class:`ServiceIndexResourceResponse`
        """
        self.version = version
        self.resources = resources


class ServiceIndexResourceResponse(NuGetResponse):

    json_key_map = {
        "url": "@id",
        "resource_type": "@type"
    }

    def __init__(self, url, resource_type, comment=None):
        """
        url : str
        resource_type : str
        comment : str, optional
        """
        self.url = url
        self.resource_type = resource_type
        self.comment = comment


class SearchResponse(NuGetResponse):

    json_key_map = {
        "total_hits": "totalHits",
    }

    def __init__(self, total_hits, data):
        """
        total_hits : int
        data : list of :class:`SearchResultResponse`
        """
        self.total_hits = total_hits
        self.data = data


class SearchResultResponse(NuGetResponse):

    json_key_map = {
        "id_": "id",
        "icon_url": "iconUrl",
        "license_url": "licenseUrl",
        "project_url": "projectUrl",
        "total_downloads:": "totalDownloads",
    }

    def __init__(self, id_, version, versions, **kwargs):
        """
        id_ : str
        version : str
        versions : list of :class:`SearchResultVersionResponse`
        """
        # description, authors,
        # icon_url, license_url, owners, project_url, registration,
        # summary, tags, title, total_downloads, verified
        self.id_ = id_
        self.version = version
        self.versions = versions

        for key, value in kwargs.items():
            setattr(self, key, value)


class SearchResultVersionResponse(NuGetResponse):

    json_key_map = {
        "id_": "@id",
    }

    def __init__(self, id_, version, downloads):
        """
        id_ : str
        version : str
        downloads : int
        """
        self.id_ = id_
        self.version = version
        self.downloads = downloads


class MetadataResponse(NuGetResponse):
    pass


class ContentResponse(NuGetResponse):
    pass


class CatalogResponse(NuGetResponse):
    pass


def _rename_keys(obj):
    if hasattr(obj, 'json_key_map'):
        d = obj.__dict__

        # wrap in list() because we're going to be modifying things
        items = list(d.items())
        for key, value in items:
            # Delete items with no value
            if value is None:
                del d[key]
                continue

            # Map our python names to the NuGet API names.
            if key in obj.json_key_map.keys():
                new_key = obj.json_key_map[key]
                d[new_key] = d[key]
                del d[key]
        return d
    else:
        # Return the dict of the item we're processing. It will then
        # continue on through the Encoder. When another unencodable
        # object is reached, _rename_keys() will be called again.
        return obj.__dict__
