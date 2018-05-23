# -*- coding: utf-8 -*-
"""
"""

import pytest
import sqlalchemy as sa

from pynuget import db


@pytest.fixture
def session():
    engine = sa.create_engine('sqlite:///:memory:')

    db.Base.metadata.create_all(engine)

    session = sa.orm.Session(bind=engine)

    # Add some dummy data
    pkg = db.Package(name="dummy", latest_version="0.0.3")
    session.add(pkg)
    session.commit()

    session.add(db.Version(package_id=pkg.package_id, version="0.0.1"))
    session.add(db.Version(package_id=pkg.package_id, version="0.0.2"))
    session.add(db.Version(package_id=pkg.package_id, version="0.0.3"))
    session.commit()

    return session


def test_create_schema(session):
    pass


def test_count_packages(session):
    session.add(db.Package(name="pkg_2", latest_version="0.0.1"))
    session.commit()
    assert db.count_packages(session) == 2


def test_search_packages(session):
    # Test with no args
    result = db.search_packages(session)
    assert len(result) == 3
    assert type(result[0]) == db.Version
    assert result[0].package.latest_version == "0.0.3"

    # add a little more dummy data
    pkg = db.Package(name="test_proj", latest_version="0.1.3")
    session.add(pkg)
    session.commit()

    session.add(db.Version(package_id=pkg.package_id, version="0.1.3"))
    session.commit()

    # Test with a search query. Note that the wildcards are added by
    # the function, and so they're not needed.
    result = db.search_packages(session, search_query='test')
    assert len(result) == 1
    assert result[0].package.name == "test_proj"

    # Test with a filter.
    result = db.search_packages(session,
                                filter_='IsLatestVersion',
                                search_query='%dummy%')
    assert len(result) == 1
    assert result[0].version == "0.0.3"

    # Test with a different order_by
    result = db.search_packages(session,
                                order_by=sa.desc(db.Version.version))
    assert len(result) == 4
    assert result[0].version == '0.1.3'
    assert result[-1].version == '0.0.1'


def test_package_updates(session):
    # Add more more dummy data
    pkg = db.Package(name="test_proj", latest_version="0.1.4")
    session.add(pkg)
    session.commit()

    session.add(db.Version(package_id=pkg.package_id, version="0.1.3"))
    session.add(db.Version(package_id=pkg.package_id, version="0.1.4"))
    session.commit()

    data = {1: '0.0.2', 2: '0.1.3'}

    result = db.package_updates(session, data)
    assert len(result) == 2
    assert type(result[0]) == db.Version
    assert result[0].package.name == "dummy"
    assert result[0].version == "0.0.3"
    assert result[1].package.name == "test_proj"
    assert result[1].version == "0.1.4"

    # if we currently have the latest version, return nothing. Do not return
    # packages that we don't have installed.
    data = {1: '0.0.3'}
    result = db.package_updates(session, data)
    assert len(result) == 0


def test_find_by_pkg_name(session):
    result_1 = db.find_by_pkg_name(session, 'dummy')
    assert type(result_1) == list
    assert len(result_1) == 3
    assert type(result_1[0]) == db.Version
    result_2 = db.find_by_pkg_name(session, 'dummy', "0.0.1")
    assert len(result_2) == 1
    assert result_2[0].version == "0.0.1"


def test_validate_id_and_version(session):
    result_1 = db.validate_id_and_version(session, 'dummy', "0.0.1")
    assert result_1 is True
    result_2 = db.validate_id_and_version(session, 'dummy', "9.9.9")
    assert result_2 is False


def test_increment_download_count(session):
    # Get the previous values
    version_sql = (session.query(db.Version.version_download_count)
                   .filter(db.Version.version_id == 1))
    package_sql = (session.query(db.Package.download_count)
                   .filter(db.Package.name == 'dummy'))
    prev_version_count = version_sql.scalar()
    prev_package_count = package_sql.scalar()

    # Run the function
    db.increment_download_count(session, 'dummy', '0.0.1')

    # Make our asserations
    assert prev_version_count + 1 == version_sql.scalar()
    assert prev_package_count + 1 == package_sql.scalar()


def test_insert_or_update_package(session):
    name = "NewPackage"
    title = "Some Title"
    latest_version = "0.0.1"

    # Test Insert
    db.insert_or_update_package(session, name, title, latest_version)

    sql = (session.query(db.Package)
           .filter(db.Package.name == name)
           )

    result = sql.scalar()
    assert isinstance(result, db.Package)
    assert result.name == name
    assert result.title == title
    assert result.latest_version == latest_version
    assert result.download_count == 0

    # Test update
    db.insert_or_update_package(session, name, "New Title", "0.0.2")
    result = sql.scalar()
    assert result.title == "New Title"
    assert result.latest_version == '0.0.2'
    assert result.download_count == 0


def test_insert_version(session):
    sql = session.query(sa.func.count(db.Version.version_id))
    version_count = sql.scalar()

    db.insert_version(session, package_id=1,
                      version="0.0.1")

    # Make sure it was added
    assert version_count + 1 == sql.scalar()


def test_delete_version(session):
    # get our initial counts
    version_count = session.query(sa.func.count(db.Version.version_id))
    package_count = session.query(sa.func.count(db.Package.package_id))
    initial_version_count = version_count.scalar()
    initial_package_count = package_count.scalar()

    # Delete a version
    pkg_id = 'dummy'
    db.delete_version(session, pkg_id, '0.0.2')

    assert initial_version_count - 1 == version_count.scalar()
    assert initial_package_count == package_count.scalar()
    assert '0.0.2' not in session.query(db.Version.version).all()

    # twice more, the 2nd of which should delete the package
    db.delete_version(session, pkg_id, '0.0.3')
    db.delete_version(session, pkg_id, '0.0.1')
    assert version_count.scalar() == 0
    assert package_count.scalar() == 0
