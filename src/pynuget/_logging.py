# -*- coding: utf-8 -*-
"""
Logging setup and handlers.
"""
import zlib
import logging
import os
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler


LOG_LEVEL_BASE = logging.DEBUG
LOG_LEVEL_FILE = LOG_LEVEL_BASE
LOG_LEVEL_CONSOLE = logging.DEBUG
LOG_LEVEL_GUI = LOG_LEVEL_BASE

LOG_FMT = ("%(asctime)s.%(msecs)03dZ"
           " [%(levelname)-8.8s]"
           " [%(module)-8.8s]"       # Note implicit string concatenation.
           " [%(funcName)-16.16s]"
           "  %(message)s"
           )
DATE_FMT = "%Y-%m-%dT%H:%M:%S"


class CustomLoggingFormatter(logging.Formatter):
    """
    Custom logging formatter. Overrides funcName and module if a value
    for name_override or module_override exists.
    """
    # Make sure things are saved in UTC.
    converter = time.gmtime

    def format(self, record):
        if hasattr(record, 'name_override'):
            record.funcName = record.name_override
        if hasattr(record, 'module_override'):
            record.module = record.module_override

        return super(CustomLoggingFormatter, self).format(record)


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


def setup_logging(to_console=True, to_file=False, log_path=None):
    # Create the logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL_BASE)

    if to_console:
        _setup_console_logging(logger)

    if to_file:
        _setup_file_logging(logger, log_path)

    return logger


def _setup_file_logging(logger, log_path):
    # Create paths and files as needed.
    log_path = Path(log_path)
    os.makedirs(log_path.parent, mode=0x0755, exist_ok=True)
    log_path.touch(mode=0o0664, exist_ok=True)

    handler = RotatingFileHandler(str(log_path), maxBytes=1e7)
    handler.rotator = _gzip_rotator
    handler.namer = _gzip_namer
    handler.setLevel(LOG_LEVEL_FILE)
    formatter = CustomLoggingFormatter(LOG_FMT, DATE_FMT)
    handler.setFormatter(formatter)
    name = "File Handler"
    handler.set_name(name)
    if name not in [h.name for h in logger.handlers]:
        logger.addHandler(handler)
        logger.info("File logging initialized")


def _setup_console_logging(logger):
    """Set up logging to the console."""
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL_CONSOLE)
    formatter = CustomLoggingFormatter(LOG_FMT, DATE_FMT)
    handler.setFormatter(formatter)
    name = "Console Handler"
    handler.set_name(name)
    if name not in [h.name for h in logger.handlers]:
        logger.addHandler(handler)
        logger.info("Console logging initialized")
