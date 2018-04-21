#!/usr/bin/python3
import sys
import logging
import site

site.addsitedir('')

logging.basicConfig(stream=sys.stderr)

from pynuget import app as application
