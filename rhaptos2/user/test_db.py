#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
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
CONFD_PATH = os.path.join(HERE, "../../local.ini")
from rhaptos2.common.configuration import (
    find_configuration_file,
    Configuration,
    )
config = Configuration.from_file(CONFD_PATH)
backend.initdb(config)  #only do thios once per applicaiton not per test


############### admin tools for nose
def setup():
    clean_dbase() 
    populate_dbase()
            
def teardown():
    backend.db_session.remove()

def clean_dbase():
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % config);
    c = conn.cursor()
    c.execute("TRUNCATE TABLE public.cnxidentifier CASCADE;")
    conn.commit()
    c.execute("TRUNCATE TABLE public.cnxuser CASCADE;")
    conn.commit()
    conn.close()


def mkuser(openidstr, fullname, force_id):
    u = usermodel.User()
    u.fullname=fullname
    u.user_id = force_id
    i = usermodel.Identifier()
    i.identifierstring = openidstr
    i.identifiertype = 'openid'
    i.user_id = u.user_id
    u.identifiers=[i,]

    db_session.add(u)
    db_session.commit()


def populate_dbase():
    """ NB - these are copy of decl.py in repo.
    Co-ordinate carefully"""

    mkuser("https://paulbrian.myopenid.com", "Paul Brian",
           "cnxuser:75e06194-baee-4395-8e1a-566b656f6920")
    mkuser("https://rossreedstrom.myopenid.com", "Ross Reedstrom",
           "cnxuser:75e06194-baee-4395-8e1a-566b656f6921")
    mkuser("https://edwoodward.myopenid.com", "Ed Woodward",
           "cnxuser:75e06194-baee-4395-8e1a-566b656f6922")
    mkuser("https://philschatz.myopenid.com", "Phil Schatz",
           "cnxuser:75e06194-baee-4395-8e1a-566b656f6923")
    mkuser("https://michaelmulich.myopenid.com", "Michael Mulich",
           "cnxuser:75e06194-baee-4395-8e1a-566b656f6924")



   
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
#    d = {"interests": null, "identifiers": [{"identifierstring": "https://paulbrian.myopenid.com", "user_id": "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920", "identifiertype": "openid"}], "user_id": "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920", "suffix": null, "firstname": null, "title": null, "middlename": null, "lastname": null, "imageurl": null, "otherlangs": null, "affiliationinstitution_url": null, "email": null, "version": null, "location": null, "recommendations": null, "preferredlang": null, "fullname": "Paul Brian", "homepage": null, "affiliationinstitution": null, "biography": null}

    d = {"user_id": "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920",
         "email": "wibbleemail", 
         "version": "1.0", 
         "fullname": "wibblename"}

    u = usermodel.put_user(d, "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    
    assert u.fullname == "wibblename"
    db_session.add(u); db_session.commit()    
    u_fromdb = usermodel.get_user("org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    assert u_fromdb.fullname == "wibblename"    




