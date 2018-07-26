# -*- coding: utf-8 -*-
"""
"""
from pynuget._logging import setup_logging
logger = setup_logging(to_console=True)

from pynuget.app_factory import create_app

__version__ = "0.2.4"
