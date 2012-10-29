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

shell_conf = { 'rhaptos2user_pgdbname': 'repouser',
 'rhaptos2user_pghost': 'devlog.office.mikadosoftware.com',
 'rhaptos2user_pgpassword': 'pass1',
 'rhaptos2user_pgpoolsize': '5',
 'rhaptos2user_pgusername': 'repouser'}

backend.initdb(shell_conf)


print "You are now in shall, without access to Flask APp, bnut with dbase"



