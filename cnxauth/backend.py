# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
from sqlalchemy import (
    or_,
    Table, Column, ForeignKey,
    Integer, String, Text, Enum,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    sessionmaker, scoped_session,
    relationship,
    )


DBSession = scoped_session(sessionmaker())
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    # title = Column(String)
    # firstname = Column(String)
    # middlename = Column(String)
    # lastname = Column(String)
    # suffix = Column(String)
    fullname = Column(String)
    # interests = Column(String)
    # affiliationinstitution_url = Column(String)
    # affiliationinstitution = Column(String)
    # preferredlang = Column(String)
    # otherlangs = Column(String)
    # imageurl = Column(String)
    # location = Column(String)
    # biography = Column(String)
    # recommendations = Column(String)
    # homepage = Column(String)
    email = Column(String)

    identifiers  = relationship("Identifier", backref="users")

    def __repr__(self):
        return "%s-%s" % (self.fullname, self.id)


class Identifier(Base):
    __tablename__   = "identifiers"

    id = Column(Integer, primary_key=True)
    identifier = Column(String, nullable=False, unique=True)
    type = Column(String)  # (Enum, "persona", "openid")
    # user_id = Column(String, ForeignKey("users.id"))


    def __init__(self, id=None, type=None):
        """ """
        self.id = id
        self.type = type

    def __repr__(self):
        return "<{} '{}'>".format(self.__class__.__name__, self.id)
