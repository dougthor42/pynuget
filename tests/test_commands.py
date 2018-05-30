# -*- coding: utf-8 -*-
"""
"""
import os
import shutil
from pathlib import Path

import pytest

from pynuget import commands
from pynuget import db

from .test_db import session


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture
def package_data():
    """A dummy set of packages."""
    data = {'PkgA': ['vers1', 'vers2', 'vers3'],
            'PkgB': ['versionA', 'VersionB', '0.0.3'],
            }
    return data


@pytest.fixture
def package_dir(package_data):
    """A dummy package directory with packages."""
    pkg_dir = Path(DATA_DIR) / Path('pkgs')
    for pkg, versions in package_data.items():
        for version in versions:
            path = pkg_dir / Path(pkg) / Path(version)
            os.makedirs(str(path), exist_ok=True)
    yield pkg_dir
    shutil.rmtree(str(pkg_dir), ignore_errors=False)


def test__get_packages_from_files(package_data, package_dir):
    data = commands._get_packages_from_files(package_dir)
    for key, value in data.items():
        assert key in package_data
        assert set(value) == set(package_data[key])


def test__db_data_to_dict(session):
    expected = {'dummy': ['0.0.1', '0.0.2', '0.0.3']}
    data = db.search_packages(session, include_prerelease=True)
    result = commands._db_data_to_dict(data)
    for key, value in result.items():
        assert key in expected
        assert set(value) == set(expected[key])
