# -*- coding: utf-8 -*-
"""
"""
import os
from pathlib import Path

import pytest
from freezegun import freeze_time

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


@freeze_time("2018-05-06 14:56:43")
def test__now_str():
    assert commands._now_str() == "180506-145643"


@freeze_time("2018-05-06 14:56:43")
def test__copy_file_with_replace_prompt__replace(dummy_file):
    # src/dummy_file will be cleaned up by the fixture.
    src = dummy_file
    dst = Path("aaa.txt")
    # make sure our dst already exists
    dst.touch()

    result = commands._copy_file_with_replace_prompt(src, dst, True)

    # the original dst should have been renamed.
    old_file = Path(str(dst) + "." + "180506-145643")
    assert old_file.exists()
    assert dst.exists()
    assert result is True

    dst.unlink()
    old_file.unlink()

    # Sanity check that everything's cleaned up.
    assert not dst.exists()
    assert not old_file.exists()


@freeze_time("2018-05-06 14:56:43")
def test__copy_file_with_replace_prompt__not_replace(dummy_file):
    # TODO: fix the copypasta.

    # src/dummy_file will be cleaned up by the fixture.
    src = dummy_file
    dst = Path("aaa.txt")
    # make sure our dst already exists
    dst.touch()

    result = commands._copy_file_with_replace_prompt(src, dst, False)

    # the original dst should *not* have been renamed.
    old_file = Path(str(dst) + "." + "180506-145643")
    assert not old_file.exists()
    assert dst.exists()
    assert result is False

    dst.unlink()

    # Sanity check that everything's cleaned up.
    assert not dst.exists()


@freeze_time("2018-05-06 14:56:43")
def test__copy_file_with_replace_prompt__not_already_exists(dummy_file):
    # TODO: fix the copypasta.

    # src/dummy_file will be cleaned up by the fixture.
    src = dummy_file
    dst = Path("aaa.txt")

    result = commands._copy_file_with_replace_prompt(src, dst, False)

    # the original dst should *not* have been renamed, because it DNE
    old_file = Path(str(dst) + "." + "180506-145643")
    assert not old_file.exists()
    assert dst.exists()
    assert result is True

    dst.unlink()

    # Sanity check that everything's cleaned up.
    assert not dst.exists()


def test__replace_prompt(monkeypatch):
    tests = [
        ('yes', True),
        ('YES', True),
        ('y', True),
        ('no', False),
        ('NO', False),
        ('n', False),
        ('', False),
    ]
    for input_, result in tests:
        monkeypatch.setattr('builtins.input', lambda x: input_)
        assert commands._replace_prompt("aaa") is result

    # Test that invalid inputs will loop. We patch `input` to count calls
    # and adjust the mocked value based on which iteration we're on.
    def counted_input(val):
        counted_input.counter += 1
        if counted_input.counter >= 2:
            return 'yes'
        return 'asdvas'
    counted_input.counter = 0

    monkeypatch.setattr('builtins.input', counted_input)
    assert commands._replace_prompt("aaa") is True


def test__enable_apache_config():
    path = Path("./apache2/sites-available/something.conf")
    enabled = Path("./apache2/sites-enabled")
    os.makedirs(str(path.parent), mode=0o2775, exist_ok=True)
    os.makedirs(str(enabled), mode=0o2775, exist_ok=True)
    path.touch()
    result = commands._enable_apache_conf(path)

    assert isinstance(result, Path)
    assert result.is_symlink()

    # Cleanup
    result.unlink()
    enabled.rmdir()
    path.unlink()
    path.parent.rmdir()
    path.parent.parent.rmdir()
