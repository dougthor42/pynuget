#!/usr/bin/python3
import sys
import logging
import site

site.addsitedir('')

logging.basicConfig(stream=sys.stderr)

from pynuget.app_factory import create_app

application = create_app()
