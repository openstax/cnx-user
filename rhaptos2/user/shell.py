#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


from rhaptos2.user import backend, usermodel
from rhaptos2.user.backend import db_session
from rhaptos2.common import conf
confd = conf.get_config("../../local.ini")


backend.initdb(confd)

print confd['rhaptos2user']
print "You are now in shall, without access to Flask APp, bnut with dbase"

u = usermodel.User()
u.fullname="Test Rhaptos user"


i = usermodel.Identifier()
i.identifierstring = 'http://rhaptos2user.myopenid.com/'
i.identifiertype = 'openid'
i.user_id = u.user_id
u.identifiers=[i,]

db_session.add(u)
db_session.commit()




