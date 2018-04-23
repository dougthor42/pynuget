# -*- coding: utf-8 -*-
"""
"""

import pytest
import sqlalchemy as sa

from pynuget import db


class TestDb(object):

    @pytest.fixture
    def session(self):
        engine = sa.create_engine('sqlite:///:memory:')

        db.Base.metadata.create_all(engine)

        session = sa.orm.Session(bind=engine)
        return session

    def test_create_schema(self, session):
        pass


    def test_count_packages(self, session):
        # insert some dummy data
        pkg = db.Package(title="dummy", latest_version="1.0.0")
        session.add(pkg)
        session.commit()

        assert db.count_packages(session) == 1
