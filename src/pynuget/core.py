# -*- coding: utf-8 -*-
"""
"""


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
