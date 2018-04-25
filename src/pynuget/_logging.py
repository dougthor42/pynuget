# -*- coding: utf-8 -*-
"""
Logging setup and handlers.
"""
import zlib
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


LOG_LEVEL_BASE = logging.DEBUG
LOG_LEVEL_FILE = LOG_LEVEL_BASE
LOG_LEVEL_CONSOLE = logging.DEBUG
LOG_LEVEL_GUI = LOG_LEVEL_BASE


# Custom namer and rotator.
# Taken from https://docs.python.org/3/howto/logging-cookbook.html
def _gzip_namer(name):
    return name + ".gz"


def _gzip_rotator(source, dest):
    # Compress the source file into our dest
    with open(source, 'rb') as open_source:
        data = open_source.read()
        compressed = zlib.compress(data)
        with open(dest, 'wb') as open_dest:
            open_dest.write(compressed)

    # Keep a copy of the most recent rotation uncompressed to make things
    # easier for users.
    os.replace(source, dest + ".1")

    os.remove(source)


def setup_logging(to_console=True, to_file=False, log_file=None):
    # Create the logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL_BASE)

    if to_console:
        _setup_console_logging(logger)

    if to_file:
        _setup_file_logging(logger, log_file)

    return logger


def _setup_file_logging(logger, log_file):

    Path(log_file).touch(mode=0o0664, exist_ok=True)

    handler = RotatingFileHandler(log_file, maxBytes=1e7)
    handler.rotator = _gzip_rotator
    handler.namer = _gzip_namer
    handler.setLevel(LOG_LEVEL_FILE)
    handler.set_name("File Handler")
    logger.addHandler(handler)

    logger.info("File logging initialized")


def _setup_console_logging(logger):
    """Set up logging to the console."""
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL_CONSOLE)
    handler.set_name("Console Handler")
    logger.addHandler(handler)

    logger.info("Console logging initialized")
