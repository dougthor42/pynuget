# -*- coding: utf-8 -*-
import os

from pynuget import app

PORT = 5000

os.environ['PYNUGET_CONFIG_TYPE'] = 'TESTING'

app.run(debug=True, port=PORT)
