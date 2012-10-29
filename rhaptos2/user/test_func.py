

import requests
import json
import time

new_user_dict = {"identifier": [{u'identifierstring': u'http://openid.cnx.org/user%s' % int(time.time()),
				u'identifiertype': u'openid',
                                u'user_id': ""
                                }],

             "id": None,
             "version": "1.0",
             "firstname": "Paul",
             "lastname" : "Test",
             "email"    : "p@cnx.org"
             }




def test_post_new_user():
    """ """
    headers = {'content-type': 'application/json'}
    payload = json.dumps(new_user_dict)
    url = "http://localhost:5000/user/"
    r = requests.post(url, data=payload, headers=headers)

    print r.text
    assert r.text == "Saved"
 
