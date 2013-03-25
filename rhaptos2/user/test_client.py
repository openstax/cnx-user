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

This is to test the user service once it is up and running on http.


We *should* be able to traverse with just the base URL, but I am not yet supplying in responses the navigation bits we need for REST.



"""
from urlparse import urljoin
import requests
import os

###### config - should be replaced with generic runner?

HERE = os.path.abspath(os.path.dirname(__file__))
CONFD_PATH = os.path.join(HERE, "../../local.ini")
from rhaptos2.common.configuration import (
    find_configuration_file,
    Configuration,
    )
config = Configuration.from_file(CONFD_PATH)

userhost=config['globals']['bamboo_global']['userserviceurl']

############################


def test_viewall():
    r = requests.get(urljoin(userhost, "users/"))
    d = r.json
    assert len(d) > 0



def test_get_known_userid():
    r = requests.get(urljoin(userhost, "user/org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920"))
    d = r.json
    assert d['fullname'] == 'Paul Brian'


def test_get_known_user_by_openid():
    r = requests.get(urljoin(userhost, "openid/?user=https://paulbrian.myopenid.com"))
    d = r.json
    assert d['fullname'] == 'Paul Brian'

def test_put():
    payload = {'email': 'testput-email', 'fullname': 'testput-fullname'}
    requests.put(urljoin(userhost, "user/org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920"))
    r = requests.get(urljoin(userhost, "openid/?user=https://paulbrian.myopenid.com"))
    d = r.json
    assert d['fullname'] == 'testput-fullname'






