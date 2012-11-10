#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


from rhaptos2.user import usermodel
import psycopg2
from nose import with_setup
import json

from rhaptos2.common import conf
CONFD=conf.get_config("../../local.ini")
from rhaptos2.user import backend
backend.initdb(CONFD)  #only do thios once per applicaiton not per test


def setup():
    clean_dbase() #### .. todo:: in setup / teardown use rollback please
    populate_dbase()

            
def teardown():
    backend.db_session.remove()


def clean_dbase():
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % CONFD["rhaptos2user"]);
    c = conn.cursor()
    c.execute("TRUNCATE TABLE public.identifier CASCADE;")
    conn.commit()
    c.execute("TRUNCATE TABLE public.user CASCADE;")
    conn.commit()
    conn.close()

def populate_dbase():
    """ """
    ben_dict = {"identifier": [{u'identifierstring': u'http://openid.cnx.org/user1',
                                u'identifiertype': u'openid',
                                u'user_id': u'org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383'}],

             "id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383", 
             "version": "1.0", 
             "firstname": "Benjamin", 
             "lastname" : "Franklin",
             "email"    : "ben@cnx.org"
             }

    u = usermodel.User()
    u = usermodel.populate_user(ben_dict, u)
    u.user_id = ben_dict['id']
    print "adding", u, u.firstname, u.user_id
    backend.db_session.add(u)

    backend.db_session.commit()
   


##################################

def test_DbaseIsUp():
    """ """
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % CONFD["rhaptos2user"]);
    c = conn.cursor()
    c.execute("Select 1;")
    rs = c.fetchall()
    assert rs[0] == (1,)
    conn.close()


############################################################ Use SQLA now

incomingd = {u'user_id': None,
 u'firstname': u'peter',
 u'identifier': [{u'identifierstring': u'x343435',
                  u'identifiertype': u'openid',
                  u'user_id': u'x3'}],
 u'lastname': u'meee',
 u'middlename': u'R'
 }

json_new_user = json.dumps(incomingd)


@with_setup(setup, teardown)
def test_can_add_user():
    new_user_id = usermodel.post_user(None, incomingd)
    



@with_setup(setup, teardown)
def test_retrieve_known_user_id():
    jsonstr = usermodel.get_user(None, "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383")
    d = json.loads(jsonstr)
    assert d['lastname'] == 'Franklin'


@with_setup(setup, teardown)
def test_lastname_search():
    pass



