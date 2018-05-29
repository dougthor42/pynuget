# -*- coding: utf-8 -*-
"""
"""
import sys
from pathlib import Path

from flask import Flask


from ._logging import setup_logging

app = Flask(__name__)
app.config.from_object('pynuget.default_config')

# Attempt to import the instance configuration.
instance_path = Path("/var/www/pynuget/instance")
config_file = instance_path / "config.py"

if config_file.exists():
    app.config.from_pyfile(str(config_file))

logger = setup_logging(to_console=True,
                       to_file=False,
                       log_path=app.config['LOG_PATH'],
                       )

msg = "Instance Config file `{}` found: {}"
logger.info(msg.format(config_file, config_file.exists()))

# Now let's make sure that all our files are set up properly
from pynuget.commands import init                              # noqa
init(server_path=app.config['SERVER_PATH'],
     package_dir=app.config['PACKAGE_DIR'],
     db_name=app.config['DB_NAME'],
     db_backend=app.config['DB_BACKEND'],
     apache_config=app.config['APACHE_CONFIG'],
     )

# contrary to Python style, the view imports must be *after* the application
# object is created.
# http://flask.pocoo.org/docs/0.11/patterns/packages/#simple-packages
try:
    import pynuget.routes                                      # noqa
except FileNotFoundError:
    logger.critical("Can't import pynuget.routes. Aborting.")
    sys.exit(1)
