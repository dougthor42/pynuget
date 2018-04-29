# -*- coding: utf-8 -*-
"""
"""
import base64
import hashlib
import tempfile
import os
import shutil
from pathlib import Path
from uuid import uuid4

from pynuget import app
from pynuget import logger


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
                     'id': str(dependency['id']),
                     'version': str(dependency['version']),
                     }
                dependencies.append(d)
        dep_fw = dep.findall('nuspec:group', namespace)
        if dep_fw:
            logger.debug("Found dependencies specific to a framework")
            for group in dep_fw:
                group_elem = group.findall('nuspec:dependency', namespace)
                for dependency in group_elem:
                    d = {'framework': str(group['targetFramework']),
                         'id': str(dependency['id']),
                         'version': str(dependency['version']),
                         }
                    dependencies.append(d)
    else:
        logger.debug("No dependencies found.")

    return dependencies


def hash_and_encode_file(file, id_, version):
    """
    Parameters
    ----------
    file : :class:`werkzeug.datastructures.FileStorage` object
        The file as retrieved by Flask.
    id_ : :class:`xml.etree.ElementTree.Element` object
    version : :class:`xml.etree.ElementTree.Element` object
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
                                  id_.text,
                                  version.text + ".nupkg",
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
            return "api_error: Unable to save file"
        else:
            logger.info("Succesfully saved package to '%s'" % local_path)

    return hash_, filesize
