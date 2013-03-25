#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


"""

Calling structure

This may seem complex (it is) but it is at least clear and avoids the usual 
complicated waving of SQLAlchmey

1. THe models exist in usermodel.
2. The session mgmt is in backend (maybe rename)
3. The two together should be setup in db_controller (A nod to MVC)
   import the session, use it to save models.




This focuses on postgres


Ship.__table__.columns will provide you with columns information
Ship.__table__.foreign_keys will list foreign keys
Ship.__table__.constraints, Ship.__table__.indexes are other properties you might find useful

# Basics - I want to 
#1. Set up a simple working version that 
#2. setup tests
#3. get a jsonifiable solution to support 1:m and M;N relations
#4. work this as standa lone with tests so it can bio-directionally deal with User JSON and later modul#e JSON
#   and do so standalone in tests
#http://docs.sqlalchemy.org/en/rel_0_7/orm/relationships.html


"""


from sqlalchemy import create_engine, MetaData, Table, ForeignKey
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship



### Module globals.  Following Pylons lead, having global
### scoped_session will ensure threads (and thread locals in Flask)
### all have theit own sessions



db_session = scoped_session(sessionmaker(autoflush=True,
                                      autocommit=False,))
Base = declarative_base()


### As long as we subclass everything from Base, we are following
### ndeclarative pattern recommended


def connect_now(confd):
    connstr = "postgresql+psycopg2://%(pgusername)s:%(pgpassword)s@%(pghost)s/%(pgdbname)s" % confd
    engine = create_engine(connstr)
    return engine


def initdb(confd):

    global db_session    
    engine = connect_now(confd)
    db_session.configure(bind=engine) 
    Base.metadata.create_all(engine)    
    

