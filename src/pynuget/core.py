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
