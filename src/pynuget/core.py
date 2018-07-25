# -*- coding: utf-8 -*-
"""
"""
import base64
import hashlib
import os
import re
from pathlib import Path
from zipfile import ZipFile

from flask import current_app
from lxml import etree as et

from pynuget import logger


class PyNuGetException(Exception):
    pass


class ApiException(PyNuGetException):
    pass


def require_auth(headers):
    """Ensure that the API key is valid."""
    key = headers.get('X-Nuget-Apikey', None)
    is_valid = key is not None and key in current_app.config['API_KEYS']
    if not is_valid:
        logger.error("Missing or Invalid API key")
    return is_valid


def get_package_path(package_id, version):
    """
    Get the file path for the specified pkg version.

    Parameters
    ----------
    package_id : str
        The name of the package
    version : str
        The package version

    Returns
    -------
    :class:`pathlib.Path`
        Relative path to the package file.
    """
    result = Path(package_id) / (version + '.nupkg')
    return result


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
    if et.iselement(dep):
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


def hash_and_encode_file(file):
    """
    Parameters
    ----------
    file : :class:`pathlib.Path` object

    Returns:
    --------
    hash_ : bytes
    filesize : int
    """
    return encode_file(file, hash_file(file, hashlib.sha512))


def hash_file(file, algorithm=hashlib.md5):
    """
    Parameters
    ----------
    file : :class:`pathlib.Path` object
    algorithm : Hash algorithm constructor
        One of the hash algorithms present in the `hashlib` module.

    Returns:
    --------
    hash_ : bytes

    Note that the returned `hash_` value is in binary. To make it a human
    readable string, use `binascii.hexlify(hash_).decode('utf-8')`.
    """
    file = str(file)
    logger.debug("Hashing file %s" % file)
    m = algorithm()
    with open(file, 'rb') as openf:
        m.update(openf.read())
    hash_ = m.hexdigest()

    logger.debug("%s hash: %s, %s" % (algorithm.__name__, hash_, file))

    return m.digest()


def encode_file(file, hash_):
    """
    Parameters
    ----------
    file : :class:`pathlib.Path` object
    hash_ : bytes
        The value returned by `hash_file()`.

    Returns:
    --------
    hash_ : bytes
    filesize : int
    """
    logger.debug("Encoding in Base64.")
    hash_ = base64.b64encode(hash_)

    # Get the filesize of the uploaded file. Used later.
    filesize = os.path.getsize(file)
    logger.debug("File size: %d bytes" % filesize)

    return hash_.decode('utf-8'), filesize


def save_file(file, pkg_name, version):
    """
    Parameters
    ----------
    file : :class:`werkzeug.datastructures.FileStorage` object
        The file as retrieved by Flask.
    pkg_name : str
    version : str

    Returns:
    --------
    local_path : :class:`pathlib.Path`
        The path to the saved file.
    """
    # Save the package file to the local package dir. Thus far it's
    # just been floating around in magic Flask land.
    server_path = Path(current_app.config['SERVER_PATH'])
    package_dir = Path(current_app.config['PACKAGE_DIR'])
    local_path = server_path / package_dir
    local_path = local_path / pkg_name / (version + ".nupkg")

    # Check if the package's directory already exists. Create if needed.
    create_parent_dirs(local_path)

    logger.debug("Saving uploaded file to filesystem.")
    try:
        file.save(str(local_path))
    except Exception as err:       # TODO: specify exceptions
        logger.error("Unknown exception: %s" % err)
        raise err
    else:
        logger.info("Succesfully saved package to '%s'" % str(local_path))

    return local_path


def create_parent_dirs(path):
    """
    Create the parent directories if it doesn't already exist.

    Parameters
    ----------
    path : :class:`pathlib.Path`
    """
    os.makedirs(str(path.parent),
                mode=0o0755,
                exist_ok=True,      # do not throw an error path exists.
                )


def extract_nuspec(file):
    """
    Parameters
    ----------
    file : :class:`pathlib.Path` object or str
        The file as retrieved by Flask.
    """
    pkg = ZipFile(str(file), 'r')
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
    if not et.iselement(nuspec):
        msg = "`nuspec` expected to be type `xml...Element`. Got {}"
        raise TypeError(msg.format(type(nuspec)))

    return nuspec


def extract_namespace(nuspec):
    """
    Extract the namespce from the NuSpec file.

    Parameters
    ----------
    nuspec : :class:`lxml.etree.Element` object
        The parsed nuspec data.

    Returns
    -------
    namespace : str
    """
    namespace = nuspec.xpath('namespace-uri(.)')
    logger.debug("Found namespace: %s" % namespace)
    return namespace


def parse_nuspec(nuspec, ns=None):
    """
    Parameters
    ----------
    nuspec : :class:`lxml.etree.Element` object
        The parsed nuspec data.
    ns : string
        The namespace to search.

    Returns
    -------
    metadata : :class:`lxml.etree.Element`
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
