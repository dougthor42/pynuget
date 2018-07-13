# -*- coding: utf-8 -*-
"""
"""
import os
from pathlib import Path

from flask import Flask
from flask import g

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
        app.config.from_pyfile(str(config_file))

    # Update logging to also log to a file.
    # This *should* modify the logger that was created in __init__.py...
    if not testing:
        setup_logging(to_console=False, to_file=True,
                      log_path=app.config['LOG_PATH'])

    # Register blueprints
    app.register_blueprint(pages)

    # Now let's make sure that all our files are set up properly
    if os.getenv("PYNUGET_CONFIG_TYPE", None) == 'TESTING':
        from pynuget.commands import init                              # noqa
        init(server_path=app.config['SERVER_PATH'],
             package_dir=app.config['PACKAGE_DIR'],
             db_name=app.config['DB_NAME'],
             db_backend=app.config['DB_BACKEND'],
             apache_config=app.config['APACHE_CONFIG'],
             )

    @app.teardown_appcontext
    def teardown_db_session(exception):
        session = getattr(g, 'session', None)
        if session is not None:
            session.close()

    return app
