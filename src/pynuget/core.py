# -*- coding: utf-8 -*-
"""
"""


from pynuget import app


# XXX: Not needed?
def api_error():
    raise NotImplementedError


def require_auth(key):
    """Ensure that the API key is valid."""
    return key in app.config['API_KEYS']


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
