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

    def test_search_packages(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.search_packages()

    def test_package_updates(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.package_updates()

    def test_find_by_id(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.find_by_id()

    def test_parse_order_by(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.parse_order_by()

    def test_do_search(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.do_search()

    def test_validate_id_and_version(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.validate_id_and_version()

    def test_increment_download_count(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.increment_download_count()

    def test_insert_or_update_package(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.insert_or_update_package()

    def test_insert_version(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.insert_version()

    def test_delete_version(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.delete_version()

    def test_build_in_clause(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.build_in_clause()
