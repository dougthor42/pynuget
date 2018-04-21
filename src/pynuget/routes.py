# -*- coding: utf-8 -*-
"""
"""

from flask import Flask

from pynuget import app


@app.route('/')
def index():
    raise NotImplementedError

def push():
    raise NotImplementedError

@app.route('/count')
def count():
    raise NotImplementedError

@app.route('/delete')
def delete():
    raise NotImplementedError

@app.route('/download')
def download():
    raise NotImplementedError

@app.route('find_by_id')
def find_by_id:
    raise NotImplementedError

@app.route('/search')
def search():
    raise NotImplementedError

@app.route('/updates')
def updates():
    raise NotImplementedError
