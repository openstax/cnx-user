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
nose is becoming more awkward than usual to pass config around.

As such I am going to call it internally here where needed and 
otherwise just run tests.

"""


import os
import psycopg2
from nose import with_setup
import json

from rhaptos2.user import backend, usermodel
from rhaptos2.user.backend import db_session

#######

def get_config(confpath):

    HERE = os.path.abspath(os.path.dirname(__file__))
    CONFD_PATH = os.path.join(HERE, confpath)
    from rhaptos2.common.configuration import (
        find_configuration_file,
        Configuration,
        )
    config = Configuration.from_file(CONFD_PATH)
    backend.initdb(config)  
    return config




### I am relucatntly ripping out nose test stuff - I cannot sanely
### pass config through nose.
### This needs to use 

def test_client(config):
    import test_client
    userhost=config['globals']['bamboo_global']['userserviceurl']
    test_client.USERHOST = userhost
    
    test_client.test_viewall()
    test_client.test_get_known_userid()

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
    """ """
    mkuser("https://paulbrian.myopenid.com", 
            "Paul Brian", "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    mkuser("https://rossreedstrom.myopenid.com", 
            "Ross Reedstrom", "org.cnx.user-d5a29da4-652f-430a-8137-76dd7f00f213")
    mkuser("https://edwoodward.myopenid.com", 
            "Ed Woodward", "org.cnx.user-41db63c4-2452-4b7c-9c63-1942ad321113")
    mkuser("https://philschatz.myopenid.com", 
            "Phil Schatz", "org.cnx.user-1adf9d40-ad86-4432-a9e9-d74436235c42")
    mkuser("https://michaelmulich.myopenid.com", 
            "Michael Mulich", "org.cnx.user-a5e5680e-bfa8-407d-a870-61ba45683261")


   
def prepopulate():
    setup()    




if __name__ == "__main__":
    from optparse import OptionParser
    usage = "runtests.py --config=../../../local.ini"
    parser = OptionParser(usage=usage)
    parser.add_option("--config", action='store', dest='config',
                      )
    parser.add_option("--prepopulate", action='store', dest='prepopulate',
                      )

    opts, args = parser.parse_args()
    
    config = get_config(opts.config)
    if opts.prepopulate:
        prepopulate()
    else:
        test_client(config)    

