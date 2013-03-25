#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
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

print "Connecting to Database:"
print config['pghost']
print "You are now in shell, without access to Flask App, but with dbase"
print "You may want to review prepopulate.py for notes on prepopulating the dbase during development"



