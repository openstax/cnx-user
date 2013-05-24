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
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    middlename = Column(String)
    lastname = Column(String)
    email = Column(String)

    # A user can have many identities, but an identity can only be
    #   associated with one user.
    identities = relationship('Identity', back_populates='user')

    def init(self):
        self.firstname = ''
        self.middlename = ''
        self.lastname = ''
        self.email = ''

    def __repr__(self):
        return "<{} '{}' - {}>".format(self.__class__.__name__,
                                       self.fullname, self.id)

    @property
    def fullname(self):
        items = [self.firstname, self.middlename, self.lastname]
        items = [n for n in items if n]
        return ' '.join(items)


class Identity(Base):
    __tablename__   = "identities"

    id = Column(Integer, primary_key=True)

    identifier = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)  # e.g. openid, google, mozilla, etc.
    type = Column(String, nullable=False)  # e.g. openid, oauth2, persona, etc.

    profile = Column(String)  # JSON profile data
    credentials = Column(String)  # JSON credential data (e.g. oauth token)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='identities')

    def __init__(self, ident_string, name, type,
                 profile='', credentials='',user=None):
        self.identifier = ident_string
        self.name = name
        self.type = type
        self.profile = profile
        self.credentials = credentials
        if user is not None:
            self.user_id = user.id
        else:
            self.user_id = None

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)
