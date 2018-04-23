# -*- coding: utf-8 -*-
"""
"""

import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
engine = sa.create_engine('sqlite:///:memory:', echo=False)


class Package(Base):
    """
    """

    __tablename__ = "package"

    package_id = Column(Integer, primary_key=True)
    title = Column(String(256), index=True)
    download_count = Column(Integer, index=True,
                            nullable=False, default=0)
    latest_version = Column(Text())


class Version(Base):
    """
    """

    __tablename__ = "version"

    version_id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("package.package_id"))
    title = Column(Text())
    description = Column(Text())
    created = Column(Integer)
    version = Column(String(32), index=True)
    package_hash = Column(Text())
    package_hash_algorithm = Column(Text())
    dependencies = Column(Text())
    pacakge_size = Column(Integer)
    release_notes = Column(Text())
    version_download_count = Column(Integer, nullable=False, default=0)
    tags = Column(Text())
    license_url = Column(Text())
    project_url = Column(Text())
    icon_url = Column(Text())
    authors = Column(Text())
    owners = Column(Text())
    require_license_acceptance = Column(Boolean())
    copyright = Column(Text())
    is_prerelease = Column(Boolean())

    package = relationship("Package", back_populates="versions")

    def __repr__(self):
        return "<Version({}, {})>".format(self.package.title, self.version)


def count_packages(session):
    return session.query(func.count(Package.package_id))


def search_packages():
    raise NotImplementedError


def package_updates():
    raise NotImplementedError


def find_by_id(session, package_id, version=None):
    query = session.query(Package).filter(Package.package_id == package_id)
    if version:
        query.filter(Package.version == version)
    query.order_by(desc(Version.version))

    return query.all()


def do_search():
    raise NotImplementedError


def validate_id_and_version():
    raise NotImplementedError


def insert_or_update_package():
    raise NotImplementedError


def insert_version():
    raise NotImplementedError


def delete_version():
    raise NotImplementedError


def build_in_clause():
    raise NotImplementedError
