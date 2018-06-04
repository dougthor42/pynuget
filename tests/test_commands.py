# -*- coding: utf-8 -*-
"""
"""
import os

import pytest

from pynuget import commands
from pynuget import db

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


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
