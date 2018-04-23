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
    pkg = db.Package(title="dummy", latest_version="0.0.3")
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
    session.add(db.Package(title="pkg_2", latest_version="0.0.1"))
    session.commit()
    assert db.count_packages(session) == 2


def test_search_packages(session):
    # Test with no args
    result = db.search_packages(session)
    assert len(result) == 3
    assert type(result[0]) == db.Version
    assert result[0].package.latest_version == "0.0.3"

    # add a little more dummy data
    pkg = db.Package(title="test_proj", latest_version="0.1.3")
    session.add(pkg)
    session.commit()

    session.add(db.Version(package_id=pkg.package_id, version="0.1.3"))
    session.commit()

    # Test with a search query. Note that the wildcards are added by
    # the function, and so they're not needed.
    result = db.search_packages(session, search_query='test')
    assert len(result) == 1
    assert result[0].package.title == "test_proj"

    # Test with a filter.
    result = db.search_packages(session,
                                filter_='is_latest_version',
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
    with pytest.raises(NotImplementedError) as e_info:
        db.package_updates()


def test_find_by_id(session):
    result_1 = db.find_by_id(session, 1)
    assert type(result_1) == list
    assert len(result_1) == 3
    assert type(result_1[0]) == db.Version
    result_2 = db.find_by_id(session, 1, "0.0.1")
    assert len(result_2) == 1
    assert result_2[0].version == "0.0.1"


def test_parse_order_by(session):
    with pytest.raises(NotImplementedError) as e_info:
        db.parse_order_by()


def test_do_search(session):
    with pytest.raises(NotImplementedError) as e_info:
        db.do_search()


def test_validate_id_and_version(session):
    result_1 = db.validate_id_and_version(session, 1, "0.0.1")
    assert result_1 is True
    result_2 = db.validate_id_and_version(session, 1, "9.9.9")
    assert result_2 is False


def test_increment_download_count(session):
    # Get the previous values
    version_sql = (session.query(db.Version.version_download_count)
                   .filter(db.Version.version_id == 1))
    package_sql = (session.query(db.Package.download_count)
                   .filter(db.Package.package_id == 1))
    prev_version_count = version_sql.scalar()
    prev_package_count = package_sql.scalar()

    # Run the function
    db.increment_download_count(session, 1, '0.0.1')

    # Make our asserations
    assert prev_version_count + 1 == version_sql.scalar()
    assert prev_package_count + 1 == package_sql.scalar()


def test_insert_or_update_package(session):
    with pytest.raises(NotImplementedError) as e_info:
        db.insert_or_update_package()


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
    pkg_id = 1
    db.delete_version(session, pkg_id, '0.0.2')

    assert initial_version_count - 1 == version_count.scalar()
    assert initial_package_count == package_count.scalar()
    assert '0.0.2' not in session.query(db.Version.version).all()

    # twice more, the 2nd of which should delete the package
    db.delete_version(session, 1, '0.0.3')
    db.delete_version(session, 1, '0.0.1')
    assert version_count.scalar() == 0
    assert package_count.scalar() == 0


def test_build_in_clause(session):
    with pytest.raises(NotImplementedError) as e_info:
        db.build_in_clause()
