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
from testconfig import config

def test_DbaseIsUp():
    """ """
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % config['app']);
    c = conn.cursor()
    c.execute("Select 1;")
    rs = c.fetchall()
    assert rs[0] == (1,)
    conn.close()

