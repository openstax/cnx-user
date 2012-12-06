#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


import psycopg2
from nose import with_setup
import json

from rhaptos2.user import backend, usermodel
from rhaptos2.user.tests.setupfortests import setup, teardown
from rhaptos2.user.backend import db_session
import os
### This probably not best instantiated here. But nose not easy to work around


from testconfig import config


############################################################ Use SQLA now

#### Testing the usermodel


@with_setup(setup, teardown)
def test_retrieve_known_user_id():
    uobj = usermodel.get_user(
              "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    assert uobj.fullname == 'Paul Brian'


@with_setup(setup, teardown)
def test_lastname_search():
    raise Exception



@with_setup(setup, teardown)
def test_putuser():

    d = {"user_id": "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920",
         "email": "wibbleemail", 
         "version": "1.0", 
         "fullname": "wibblename"}

    u = usermodel.put_user(d, "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    
    assert u.fullname == "wibblename"
    db_session.add(u); db_session.commit()    
    u_fromdb = usermodel.get_user("org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    assert u_fromdb.fullname == "wibblename"    
