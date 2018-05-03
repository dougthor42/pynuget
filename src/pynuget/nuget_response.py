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


class MetadataIndexResponse(NuGetResponse):

    def __init__(self, count, items):
        """
        count : int
        items : array of RegistrationPage objects
        """
        self.count = count
        self.items = items


class MetadataIndexPage(NuGetResponse):

    json_key_map = {
        "id_": "@id",
    }

    def __inti__(self, id_, count, lower, upper, items=None, parent=None):
        """
        id_ : string
        count : int
        lower : string
        upper : string
        items : array of MetadataIndexLeaf objects
        parent : string
        """
        self.id_ = id_
        self.count = count
        self.lower = lower
        self.upper = upper
        self.items = items
        self.parent = parent


class MetadataIndexLeaf(NuGetResponse):

    json_key_map = {
        "id_": "@id",
        "catalog_entry": "catalogEntry",
        "pacakge_content": "pacakgeContent",
    }

    def __init__(self, id_, catalog_entry, package_content):
        """
        id_ : str
        catalog_entry : CatalogEntry object
        pacakge_content : str
        """
        self.id_ = id_
        self.catalog_entry = catalog_entry
        self.pacakge_content = package_content


class CatalogEntry(NuGetResponse):

    json_key_map = {
        "id_": "@id",
        "pkg_id": "id",
        "dependency_groups": "dependencyGroups",
        "icon_url": "iconUrl",
        "license_url": "licenseUrl",
        "min_client_version": "minClientVersion",
        "project_url": "projectUrl",
        "require_license_acceptance": " requireLicenseAcceptance",
    }

    def __init__(self, id_, pkg_id, version, **kwargs):
        """
        id_ : str
        pkg_id : str
        vesion : str
        authors : str or list of str
        dependency_groups : array of PackageDependencyGroup objects
        description : str
        icon_url : str
        license_url : str
        listed : bool
        min_client_version : str
        project_url : str
        published : str (ISO 8601 timestamp)
        require_license_acceptance : bool
        summary : str
        tags : str or list of str
        title : str
        """
        self.id_ = id_
        self.pkg_id = pkg_id
        self.version = version
        for key, value in kwargs.items():
            setattr(self, key, value)


class PackageDependencyGroup(NuGetResponse):

    json_key_map = {
        "target_framework": "targetFramework",
    }

    def __init__(self, target_framework, dependencies=None):
        """
        target_framework : str
        dependencies : array of PackageDependency objects
        """
        self.target_framework = target_framework
        self.dependencies = dependencies


class PackageDependency(NuGetResponse):

    json_key_map = {
        "id_": "id",
        "range_": "range",
    }

    def __init__(self, id_, range_=None, registration=None):
        """
        id_ : str
        range_ : str (version range)
        registration : str
        """
        self.id_ = id_
        self.range_ = range_
        self.registration = registration


class RegistrationPageResponse(NuGetResponse):

    json_key_map = {
        "id_": "@id",
    }

    def __inti__(self, id_, count, lower, upper, items, parent):
        """
        id_ : string
        count : int
        lower : string
        upper : string
        items : array of MetadataIndexLeaf objects
        parent : string
        """
        self.id_ = id_
        self.count = count
        self.lower = lower
        self.upper = upper
        self.items = items
        self.parent = parent


class RegistrationLeafResponse(NuGetResponse):

    json_key_map = {
        "id_": "@id",
        "catalog_entry": "catalogEntry",
        "pacakge_content": "pacakgeContent",
    }

    def __init__(self, id_, **kwargs):
        """
        id_ : str
        catalog_entry : str
        listed : bool
        pacakge_content : str
        published : str (ISO 8601 timestamp)
        registration : str
        """
        self.id_ = id_
        for key, value in kwargs.items():
            setattr(self, key, value)


class ContentResponse(NuGetResponse):

    def __init__(self, versions):
        """
        versions : array of str
        """
        self.versions = versions


class CatalogIndexResponse(NuGetResponse):

    json_key_map = {
        "commit_id": "commitId",
        "commit_timestamp": "commitTimeStamp",
    }

    def __init__(self, commit_id, commit_timestamp, count, items):
        """
        commit_id : str
        commit_timestamp : str
        count : int
        itesm : list of CatalogIndexPage objects
        """
        self.commit_id = commit_id
        self.commit_timestamp = commit_timestamp
        self.count = count
        self.items = items


class CatalogIndexPage(NuGetResponse):

    json_key_map = {
        "id_": "@id",
        "commit_id": "commitId",
        "commit_timestamp": "commitTimeStamp",
    }

    def __init__(self, id_, commit_id, commit_timestamp, count):
        """
        id_ : str
        commit_id : str
        commit_timestamp : str
        count : int
        """
        self.id_ = id_
        self.commit_id = commit_id
        self.commit_timestamp = commit_timestamp
        self.count = count


class CatalogPage(NuGetResponse):

    json_key_map = {
        "commit_id": "commitId",
        "commit_timestamp": "commitTimeStamp",
    }

    def __init__(self, commit_id, commit_timestamp, count, items, parent):
        """
        commit_id : str
        commit_timestamp : str
        count : int
        items : list of CatalogItem objects
        parent : str
        """
        self.commit_id = commit_id
        self.commit_timestamp = commit_timestamp
        self.count = count
        self.items = items
        self.parent = parent


class CatalogItem(NuGetResponse):

    json_key_map = {
        "id_": "@id",
        "type_": "@type",
        "commit_id": "commitId",
        "commit_timestamp": "commitTimeStamp",
        "nuget_id": "nuget:id",
        "nuget_version": "nuget:version",
    }

    def __init__(self, id_, type_, commit_id, commit_timestamp,
                 nuget_id, nuget_version):
        """
        id_ : str
        type_ : str
        commit_id : str
        commit_timestamp : str
        nuget_id : str
        nuget_version : str
        """
        self.id_ = id_
        self.type_ = type_
        self.commit_id = commit_id
        self.commit_timestamp = commit_timestamp
        self.nuget_id = nuget_id
        self.nuget_version = nuget_version


class CatalogLeaf(NuGetResponse):

    json_key_map = {
        "type_": "@type",
        "catalog_commit_id": "catalog:commitId",
        "catalog_commit_timestamp": "catalog:commitTimeStamp",
        "id_": "id",
    }

    def __init__(self, type_, catalog_commit_id, catalog_timestamp,
                 id_, published, version):
        """
        type_ : str or array of str
        catalog_commit_id : str
        catalog_commit_timestamp : str
        id_ : str
        published : str
        version : str
        """
        self.type_ = type_
        self.catalog_commit_id = catalog_commit_id
        self.catalog_timestamp = catalog_timestamp
        self.id_ = id_
        self.published = published
        self.version = version


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
