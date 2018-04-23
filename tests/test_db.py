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
        # insert some dummy data
        pkg = db.Package(title="dummy", latest_version="1.0.0")
        session.add(pkg)
        session.commit()

        vers = db.Version(package_id=pkg.package_id, version="0.0.1")
        session.add(vers)
        session.commit()

        vers = db.Version(package_id=pkg.package_id, version="0.0.2")
        session.add(vers)
        session.commit()

        result_1 = db.find_by_id(session, vers.package_id)
        assert type(result_1) == list
        assert len(result_1) == 2
        assert type(result_1[0]) == db.Version
        result_2 = db.find_by_id(session, vers.package_id, "0.0.1")
        assert len(result_2) == 1
        assert result_2[0].version == "0.0.1"

    def test_parse_order_by(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.parse_order_by()

    def test_do_search(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.do_search()

    def test_validate_id_and_version(self, session):
        # insert some dummy data
        pkg = db.Package(title="dummy", latest_version="1.0.0")
        session.add(pkg)
        session.commit()

        vers = db.Version(package_id=pkg.package_id, version="0.0.1")
        session.add(vers)
        session.commit()

        result_1 = db.validate_id_and_version(session,
                                              vers.package_id,
                                              vers.version)
        assert result_1 is True
        result_2 = db.validate_id_and_version(session,
                                              vers.package_id,
                                              "9.9.9")
        assert result_2 is False

    def test_increment_download_count(self, session):
        # insert some dummy data
        pkg = db.Package(title="dummy", latest_version="1.0.0")
        session.add(pkg)
        session.commit()

        vers = db.Version(package_id=pkg.package_id, version="0.0.1")
        session.add(vers)
        session.commit()

        # Get the previous values
        version_sql = (session.query(db.Version.version_download_count)
                       .filter(db.Version.version_id == vers.version_id))
        package_sql = (session.query(db.Package.download_count)
                       .filter(db.Package.package_id == vers.package_id))
        prev_version_count = version_sql.scalar()
        prev_package_count = package_sql.scalar()

        # Run the function
        db.increment_download_count(session, pkg.package_id, vers.version)

        # Make our asserations
        assert prev_version_count + 1 == version_sql.scalar()
        assert prev_package_count + 1 == package_sql.scalar()

    def test_insert_or_update_package(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.insert_or_update_package()

    def test_insert_version(self, session):
        # insert some dummy data
        pkg = db.Package(title="dummy", latest_version="1.0.0")
        session.add(pkg)
        session.commit()

        sql = session.query(sa.func.count(db.Version.version_id))
        version_count = sql.scalar()

        db.insert_version(session, package_id=pkg.package_id,
                          version="0.0.1")

        # Make sure it was added
        assert version_count + 1 == sql.scalar()

    def test_delete_version(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.delete_version()

    def test_build_in_clause(self, session):
        with pytest.raises(NotImplementedError) as e_info:
            db.build_in_clause()
