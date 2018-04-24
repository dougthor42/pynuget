# -*- coding: utf-8 -*-
"""
"""


# XXX: Not needed?
def api_error():
    raise NotImplementedError


# XXX: Not needed?
def require_auth():
    """Ensure that the API key is valid."""
    raise NotImplementedError


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
