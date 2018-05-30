# -*- coding: utf-8 -*-
import os

from pynuget.app_factory import create_app

PORT = 5000

os.environ['PYNUGET_CONFIG_TYPE'] = 'TESTING'

app = create_app()
app.run(debug=True, port=PORT)
