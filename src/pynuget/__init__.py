# -*- coding: utf-8 -*-
"""
"""

from flask import Flask

app = Flask(__name__)

# contrary to Python style, the view imports must be *after* the application
# object is created.
# http://flask.pocoo.org/docs/0.11/patterns/packages/#simple-packages
try:
    import pynuget.routes
except FileNotFoundError:
    raise
    #logger.error("Can't import pynuget.routes.")
