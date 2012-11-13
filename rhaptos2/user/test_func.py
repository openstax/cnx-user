

"""
Functionally testing the user store

INIT tests
----------
Lets start up and prepopulate the dbase

API tests
---------
Do we support the api (Currently at http://rhaptos2user.readthedocs.org/en/latest/)

Self population 
---------------

I want to POST and PUT my own details

Security tests
--------------

Not yet defined - 


"""

import requests
import json
import time

new_user_dict = {"identifier": [{u'identifierstring':"https://www.google.com/accounts/o8/id?id=AItOawm78qrJQcn7Tg7W_ZiQN7-5hhGyEovVVhw" ,
                                 #u'http://openid.cnx.org/user%s' % int(time.time()),
				u'identifiertype': u'openid',
                                u'user_id': ""
                                },
                                {u'identifierstring':'http://rhaptos2user.myopenid.com/',
                                u'identifiertype': u'openid',
                                u'user_id': ""
                                },
                                ],

             "id": None,
             "version": "1.0",
             "firstname": "Example",
             "lastname" : "Example",
             "email"    : "example@cnx.org",
             "fullname" : "Rhaptos Example User"
             }

populate_user_template = {"identifier": [{
                                u'identifierstring': u'http://openid.cnx.org/user%s',
				u'identifiertype': u'openid',
                                u'user_id': ""
                                },
                                ],

             "id": None,
             "version": "1.0",
             "firstname": "Example",
             "lastname" : "Example",
             "email"    : "example@cnx.org",
             "fullname" : "Rhaptos Example User "
             }


def test_post_new_user2():
    """ """
    headers = {'content-type': 'application/json'}
    d = populate_user_template
    for t in range(3,100):

        d["identifier"][0][u'identifierstring'] = d["identifier"][0][u'identifierstring']%t
        d['fullname'] = "Rhatpso Example User %s" % t
        payload = json.dumps(d)
        url = "http://localhost:5000/user/"
        r = requests.post(url, data=payload, headers=headers)

        print r.text, t
        assert r.text == "Saved"


#def test_post_new_user():
#    """ """
#    headers = {'content-type': 'application/json'}
#    payload = json.dumps(new_user_dict)
#    url = "http://localhost:5000/user/"
#    r = requests.post(url, data=payload, headers=headers)#

#    print r.text
#    assert r.text == "Saved"
 
