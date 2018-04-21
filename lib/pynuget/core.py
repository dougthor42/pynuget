# -*- coding: utf-8 -*-
"""
"""

def api_error():
    raise NotImplementedError

def require_auth():
    """Ensure that the API key is valid."""
    raise NotImplementedError

def request_method():
    """Get the HTTP method used for the current request."""
    raise NotImplementedError

def get_package_path():
    """Get the file path for the specified pkg version."""
    raise NotImplementedError

def url_scheme():
    raise NotImplementedError
