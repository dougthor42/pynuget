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

ENV_VAR = "PYNUGET_CONFIG_TYPE"


def create_app():
    """
    Application Factory.
    """

    instance_path = Path("/var/www/pynuget")
    config_file = instance_path / "config.py"

    testing = os.getenv(ENV_VAR, None) == 'TESTING'

    app = Flask(__name__)
    app.config.from_object('pynuget.default_config')

    # Override some default vars if we're running using the flask dev server.
    if os.getenv(ENV_VAR, None) == "LOCAL_DEV":
        app.config['LOG_PATH'] = os.getenv('PYNUGET_LOG_PATH')
        app.config['SERVER_PATH'] = os.getenv('PYNUGET_SERVER_PATH')

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
