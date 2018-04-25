# -*- coding: utf-8 -*-
"""
Logging setup and handlers.
"""

import logging


LOG_LEVEL_BASE = logging.DEBUG
LOG_LEVEL_FILE = LOG_LEVEL_BASE
LOG_LEVEL_CONSOLE = logging.DEBUG
LOG_LEVEL_GUI = LOG_LEVEL_BASE


def setup_logging():
    pass


def _setup_file_logging():
    pass


def _setup_console_logging(logger):
    """Set up logging to the console."""
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL_CONSOLE)
    handler.set_name("Console Handler")
    logger.addHandler(handler)

    logger.info("Console logging initialized")
