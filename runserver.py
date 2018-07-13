# -*- coding: utf-8 -*-
import os

from pynuget import commands
from pynuget import default_config
from pynuget.app_factory import create_app

PORT = 5000

os.environ['PYNUGET_CONFIG_TYPE'] = 'LOCAL_DEV'

server_path = default_config.SERVER_PATH
package_dir = default_config.PACKAGE_DIR
db_name = default_config.DB_NAME
db_backend = default_config.DB_BACKEND
log_dir = default_config.LOG_DIR


commands._check_permissions()
commands._create_directories(server_path, package_dir, log_dir)
commands._create_db(db_backend, db_name, server_path)

app = create_app()
app.run(debug=True, port=PORT)
