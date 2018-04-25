# -*- coding: utf-8 -*-
"""
"""

# Third-Party
from flask import request

from pynuget import app

@app.route('/', methods=['GET'])
def root():
    raise NotImplementedError

@app.route('/index', methods=['GET', 'PUT', 'DELETE'])
def index():
    if request.method == 'PUT':
        push()


def push():
    raise NotImplementedError

@app.route('/count', methods=['GET'])
def count():
    raise NotImplementedError

@app.route('/delete', methods=['DELETE'])
def delete():
    raise NotImplementedError

@app.route('/download', methods=['GET'])
def download():
    raise NotImplementedError

@app.route('find_by_id', methods=['GET'])
def find_by_id:
    raise NotImplementedError

@app.route('/search', methods=['GET'])
def search():
    raise NotImplementedError

@app.route('/updates', methods=['GET'])
def updates():
    raise NotImplementedError
