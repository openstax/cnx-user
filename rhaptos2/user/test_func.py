

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




def test_post_new_user():
    """ """
    headers = {'content-type': 'application/json'}
    payload = json.dumps(new_user_dict)
    url = "http://localhost:8001/user/"
    r = requests.post(url, data=payload, headers=headers)

    print r.text
    assert r.text == "Saved"
 
