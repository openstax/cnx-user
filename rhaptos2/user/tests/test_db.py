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
Simple testing of API - using HTTP.
We are not instantiating the app and testing it under the covers here.

setup
-----
Create the tables if not existing
prepopulate with "test" dataset

teardown
--------
wipe and re-populate with test dataset
(should encapsulate each test in a rolling back transaction - much faster)
#### .. todo:: in setup / teardown use rollback please




"""

import psycopg2
from nose import with_setup
import json

from rhaptos2.user import backend, usermodel
from rhaptos2.user.backend import db_session
import os
### This probably not best instantiated here. But nose not easy to work around




HERE = os.path.abspath(os.path.dirname(__file__))
CONFD_PATH = os.path.join(HERE, "../../../local.ini")
from rhaptos2.common.configuration import (
    find_configuration_file,
    Configuration,
    )
config = Configuration.from_file(CONFD_PATH)




##################################

##################################

def test_DbaseIsUp():
    """ """
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % config);
    c = conn.cursor()
    c.execute("Select 1;")
    rs = c.fetchall()
    assert rs[0] == (1,)
    conn.close()


############################################################ Use SQLA now

#### Testing the usermodel


@with_setup(setup, teardown)
def test_retrieve_known_user_id():
    uobj = usermodel.get_user(
              "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    assert uobj.fullname == 'Paul Brian'


@with_setup(setup, teardown)
def test_lastname_search():
    pass



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


if __name__ == "__main__":
    setup()



