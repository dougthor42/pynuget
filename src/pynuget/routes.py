# -*- coding: utf-8 -*-
"""
"""

# Third-Party
from flask import request
from flask import Response
import sqlalchemy as sa

from pynuget import app
from pynuget import db




@app.route('/web')
def root():
    return "Hello World!"


@app.route('/', methods=['GET', 'PUT', 'DELETE'])
@app.route('/index', methods=['GET', 'PUT', 'DELETE'])
def index():
    if request.method == 'PUT':
        push()

    resp = Response("<?xml version='1.0' encoding='utf-8' standalone='yes'?>")
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


def push():
    raise NotImplementedError


@app.route('/count', methods=['GET'])
def count():
    engine = sa.create_engine('sqlite:///:memory:', echo=False)
    db.Base.metadata.create_all(engine)
    session = sa.orm.Session(bind=engine)

    resp = Response(str(db.count_packages(session)))
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


@app.route('/delete', methods=['DELETE'])
def delete():
    raise NotImplementedError


@app.route('/download', methods=['GET'])
def download():
    raise NotImplementedError


@app.route('/find_by_id', methods=['GET'])
def find_by_id():
    raise NotImplementedError


@app.route('/search', methods=['GET'])
def search():
    raise NotImplementedError


@app.route('/updates', methods=['GET'])
def updates():
    raise NotImplementedError
