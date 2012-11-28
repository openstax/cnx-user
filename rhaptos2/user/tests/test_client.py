

"""

This is to test the user service once it is up and running on http.


We *should* be able to traverse with just the base URL, but I am not yet supplying in responses the navigation bits we need for REST.



"""
from urlparse import urljoin
import requests
import os


############################
USERHOST=None

def test_viewall():
    r = requests.get(urljoin(USERHOST, "users/"))
    d = r.json
    assert len(d) > 0



def test_get_known_userid():
    r = requests.get(urljoin(USERHOST, "user/org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920"))
    d = r.json
    assert d['fullname'] == 'Paul Brian'


def test_get_known_user_by_openid():
    r = requests.get(urljoin(USERHOST, "openid/?user=https://paulbrian.myopenid.com"))
    d = r.json
    assert d['fullname'] == 'Paul Brian'

def test_put():
    payload = {'email': 'testput-email', 'fullname': 'testput-fullname'}
    requests.put(urljoin(USERHOST, "user/org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920"))
    r = requests.get(urljoin(USERHOST, "openid/?user=https://paulbrian.myopenid.com"))
    d = r.json
    assert d['fullname'] == 'testput-fullname'


def test_post():
    payload = {'email': 'testpost-email', 'fullname': 'testpost-fullname',
               'identifiers':[{'identifierstring':"FAKEOPENID", 
                               'identifiertype':  "openid"},]
              }
    requests.put(urljoin(USERHOST, "user/"))
    r = requests.get(urljoin(USERHOST, "openid/?user=FAKEOPENID"))
    d = r.json
    assert d['fullname'] == 'testpost-fullname'


