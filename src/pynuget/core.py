# -*- coding: utf-8 -*-
"""
"""
import base64
import hashlib
import json
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as et
from zipfile import ZipFile
from pathlib import Path
from uuid import uuid4

from pynuget import app
from pynuget import logger


class PyNuGetException(Exception):
    pass


class ApiException(PyNuGetException):
    pass


# XXX: Not needed?
def api_error():
    raise NotImplementedError


def require_auth(headers):
    """Ensure that the API key is valid."""
    key = headers.get('X-Nuget-Apikey', None)
    is_valid = key is not None and key in app.config['API_KEYS']
    if not is_valid:
        logger.error("Missing or Invalid API key")
    return is_valid


# XXX: Not needed?
def request_method():
    """Get the HTTP method used for the current request."""
    raise NotImplementedError


def get_package_path(package_id, version):
    """Get the file path for the specified pkg version."""
    #TODO: custom package path
    return './packagefiles/' + str(package_id) + '/' + version + '.nupkg'


# XXX: Not needed?
def url_scheme():
    raise NotImplementedError


def et_to_str(node):
    """Get the text value of an Element, returning None if not found."""
    try:
        return node.text
    except AttributeError:
        return None


def determine_dependencies(metadata_element, namespace):
    """"""
    # TODO: python-ify
    logger.debug("Parsing dependencies.")
    dependencies = []
    dep = metadata_element.find('nuspec:dependencies', namespace)
    if dep:
        logger.debug("Found dependencies.")
        dep_no_fw = dep.findall('nuspec:dependency', namespace)
        if dep_no_fw:
            logger.debug("Found dependencies not specific to any framework.")
            for dependency in dep_no_fw:
                d = {'framework': None,
                     'id': str(dependency.attrib['id']),
                     'version': str(dependency.attrib['version']),
                     }
                dependencies.append(d)
        dep_fw = dep.findall('nuspec:group', namespace)
        if dep_fw:
            logger.debug("Found dependencies specific to a framework")
            for group in dep_fw:
                group_elem = group.findall('nuspec:dependency', namespace)
                for dependency in group_elem:
                    d = {'framework': str(group.attrib['targetFramework']),
                         'id': str(dependency.attrib['id']),
                         'version': str(dependency.attrib['version']),
                         }
                    dependencies.append(d)
    else:
        logger.debug("No dependencies found.")

    return dependencies


def hash_and_encode_file(file, pkg_name, version):
    """
    Parameters
    ----------
    file : :class:`werkzeug.datastructures.FileStorage` object
        The file as retrieved by Flask.
    pkg_name : str
    version : str
    """
    logger.debug("Hashing and encoding uploaded file.")
    with tempfile.TemporaryDirectory() as tmpdir:
        name = str(uuid4()) + ".tmp"
        temp_file = os.path.join(tmpdir, name)
        logger.debug("Saving uploaded file to temporary location.")
        file.save(temp_file)
        m = hashlib.sha512()
        logger.debug("Hashing file.")
        with open(temp_file, 'rb') as openf:
            m.update(openf.read())
        logger.debug("Encoding in Base64.")
        hash_ = base64.b64encode(m.digest())

        # Get the filesize of the uploaded file. Used later.
        filesize = os.path.getsize(temp_file)
        logger.debug("File size: %d bytes" % filesize)

        # Save the package file to the local package dir. Thus far it's
        # just been floating around in magic Flask land.
        local_path = Path(app.config['SERVER_PATH']) / Path(app.config['PACKAGE_DIR'])
        local_path = os.path.join(str(local_path),
                                  pkg_name,
                                  version + ".nupkg",
                                  )

        # Check if the pacakge's directory already exists. Create if needed.
        os.makedirs(os.path.split(local_path)[0],
                    mode=0o0755,
                    exist_ok=True,      # do not throw an error path exists.
                    )

        logger.debug("Saving uploaded file to filesystem.")
        try:
            shutil.copy(temp_file, local_path)
        except Exception as err:       # TODO: specify exceptions
            logger.error("Unknown exception: %s" % err)
            raise err
        else:
            logger.info("Succesfully saved package to '%s'" % local_path)

    return hash_, filesize


def extract_nuspec(file):
    """
    Parameters
    ----------
    file : :class:`werkzeug.datastructures.FileStorage` object or path (str)
        The file as retrieved by Flask.
    """
    pkg = ZipFile(file, 'r')
    logger.debug("Parsing uploaded file.")
    nuspec_file = None
    pattern = re.compile(r'^.*\.nuspec$', re.IGNORECASE)
    nuspec_file = list(filter(pattern.search, pkg.namelist()))
    if len(nuspec_file) > 1:
        logger.error("Multiple NuSpec files found within the package.")
        raise ApiException("api_error: multiple nuspec files found")
    elif len(nuspec_file) == 0:
        logger.error("No NuSpec file found in the package.")
        raise ApiException("api_error: nuspec file not found")      # TODO
    nuspec_file = nuspec_file[0]

    with pkg.open(nuspec_file, 'r') as openf:
        nuspec_string = openf.read()
        logger.debug("NuSpec string:")
        logger.debug(nuspec_string)

    logger.debug("Parsing NuSpec file XML")
    nuspec = et.fromstring(nuspec_string)
    if not isinstance(nuspec, et.Element):
        msg = "`nuspec` expected to be type `xml...Element`. Got {}"
        raise TypeError(msg.format(type(nuspec)))

    return nuspec


def parse_nuspec(nuspec, ns=None):
    """
    Parameters
    ----------
    nuspec : :class:`xml.etree.ElementTree.Element` object
        The parsed nuspec data.
    ns : string
        The namespace to search.

    Returns
    -------
    metadata : :class:`xml.etree.ElementTree.Element`
    pkg_name : str
    version : str
    """
    metadata = nuspec.find('nuspec:metadata', ns)
    if metadata is None:
        msg = 'Unable to find the metadata tag!'
        logger.error(msg)
        raise ApiException(msg)

    # TODO: I think I need different error handling around `.text`.
    pkg_name = metadata.find('nuspec:id', ns)
    version = metadata.find('nuspec:version', ns)
    if pkg_name is None or version is None:
        logger.error("ID or version missing from NuSpec file.")
        raise ApiException("api_error: ID or version missing")        # TODO

    return metadata, pkg_name.text, version.text


def jsonify_search_results():
    pass
