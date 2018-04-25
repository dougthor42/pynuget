# -*- coding: utf-8 -*-
"""
"""

# Third-Party
from flask import g
from flask import request
from flask import Response
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from werkzeug.local import LocalProxy

from pynuget import app
from pynuget import db
from pynuget import core


def get_db_session():
    session = getattr(g, 'session', None)
    if session is None:
        # TODO: Handle pre-existing DB files.
        # TODO: Use files not memory
        engine = create_engine('sqlite:///:memory:', echo=False)
        Session = sessionmaker(bind=engine)
        db.Base.metadata.create_all(engine)
        session = g.session = Session()
    return session


@app.teardown_appcontext
def teardown_db_session(exception):
    session = getattr(g, 'session', None)
    if session is not None:
        session.close()


session = LocalProxy(get_db_session)


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
    resp = Response(str(db.count_packages(session)))
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


@app.route('/delete', methods=['DELETE'])
def delete():
    raise NotImplementedError


@app.route('/download', methods=['GET'])
def download():
    id_ = request.args.get('id')
    version = request.args.get('version')

    path = core.get_package_path(id_, version)
    db.increment_download_count(session, id_, version)
    filename = "{}.{}.nupkg".format(id_, version)

    resp = Response()
    resp.headers[''] = 'application/zip'
    resp.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    resp.headers['X-Accel-Redirect'] = path

    return resp


@app.route('/find_by_id', methods=['GET'])
def find_by_id():
    raise NotImplementedError


@app.route('/search', methods=['GET'])
def search():
    raise NotImplementedError


@app.route('/updates', methods=['GET'])
def updates():
    raise NotImplementedError
