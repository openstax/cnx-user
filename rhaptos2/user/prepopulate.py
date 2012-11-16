#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###

import os
from rhaptos2.user import backend, usermodel
from rhaptos2.user.backend import db_session
from rhaptos2.common import conf

HERE = os.path.abspath(os.path.dirname(__file__))
CONFD_PATH = os.path.join(HERE, "../../local.ini")
confd = conf.get_config(CONFD_PATH)

from rhaptos2.common.configuration import (
    find_configuration_file,
    Configuration,
    )
config = Configuration.from_file(CONFD_PATH)


backend.initdb(config)

print "Running simple prepopulation of database as connected by:"
print config['pghost']

def mkuser(fullname, openidstr):
    u = usermodel.User()
    u.fullname=fullname
    i = usermodel.Identifier()
    i.identifierstring = openidstr
    i.identifiertype = 'openid'
    i.user_id = u.user_id
    u.identifiers=[i,]

    db_session.add(u)
    db_session.commit()

#mkuser('Rhaptos2 Test User', 'http://rhaptos2user.myopenid.com/')
mkuser('foobar User', 'http://fake1.example.com/')
mkuser('wibble Test User', 'http://fake2.example.com/')

########
