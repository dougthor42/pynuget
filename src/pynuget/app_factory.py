# -*- coding: utf-8 -*-
"""
"""
import os
from pathlib import Path

from flask import Flask
from flask import g

from pynuget import logger
from pynuget._logging import setup_logging
from pynuget.routes import pages


def create_app():
    """
    Application Factory.
    """

    instance_path = Path("/var/www/pynuget")
    config_file = instance_path / "config.py"

    testing = os.getenv("PYNUGET_CONFIG_TYPE", None) == 'TESTING'

    app = Flask(__name__)
    app.config.from_object('pynuget.default_config')

    if config_file.exists():
        logger.debug("Found config file: %s. Loading..." % str(config_file))
        app.config.from_pyfile(str(config_file))

    # Update logging to also log to a file.
    # This *should* modify the logger that was created in __init__.py...
    if not testing:
        setup_logging(to_console=False, to_file=True,
                      log_path=app.config['LOG_PATH'])

    # Register blueprints
    app.register_blueprint(pages)

    @app.teardown_appcontext
    def teardown_db_session(exception):
        session = getattr(g, 'session', None)
        if session is not None:
            session.close()

    return app
