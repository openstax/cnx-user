#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


from flask import Flask, render_template, request, g, session, flash,   redirect, url_for, abort


import datetime
import md5, random
import os, sys
import flask
import statsd
import json
from functools import wraps
import uuid
import requests
import urllib

from rhaptos2.common import log
from rhaptos2.common import err
from rhaptos2.common import conf



from rhaptos2.user import get_app, dolog, usermodel, backend
app = get_app()




@app.before_request
def requestid():
    g.requestid = uuid.uuid4()
    g.request_id = g.requestid




@app.route('/')
def index():
    dolog("INFO", "THis is request %s" % g.requestid)
    return "Stub user database"

###Holy CRAP what an awful place to put this !!!
stubuserdoc={"id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383",

    "details":{"FullName": "Benjamin Franklin",
               "email":   "ben@mikadosoftware.com",
               "Address" : "36 Craven Street  London WC2N 5NF",
              },

    "identifiers": ["https://www.google.com/accounts/o8/id?id=AItOawlc7oYk8MNlwBgxCwMhLDqzXq1BXA4abbk",
                "http://openid.cnx.org/user4",
                "paul@mikadosoftware.com"
               ],
    "version": "1.0"
    }

stubjsondoc = json.dumps(stubuserdoc)




@app.route('/user/', methods=["GET",])
def get_user():
    """

    example::

      /user?user=org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383

    .. todo:: Flask will unquote the whole URL and try to route that,
              instead of taking the route that exists in quoted format,
               and then calculating the <parameter>
             
              /openid/this/is/a/path
 
              /openid/http://this/is/openid/url
    
              /openid/'http%3A%2F%2Fthis%2Fis%2Fopenid%2Furl'
           
              Flask should handle the last differently.   

    originally this use <idenfitfier> to pluckjt eh id from a path.
    However if I sent in an openid id, with / in it, even quoted, Falsk would
    pre-unquote and try to route the url now with added slashes.

    I switched to a quick fix - now passing in a quote_plus'd query string named user
    
  

    ##Write tests!
    """
    qstr = request.query_string
    
    #    unquoted_identifier = urllib.unquote(identifier)
    unquoted_identifier = qstr.replace("user=", "")

    dolog("INFO", "THis is request %s" % g.requestid)
    dolog("INFO", "I saw identifier: %s" % unquoted_identifier)

    ### errors to abort function
    ### .. todo:: better trap than abort()

    security_token = None
    try:
        json_str = usermodel.get_user(security_token, unquoted_identifier)     
    except err.Rhaptos2Error, e:
        abort(404)


    resp = flask.make_response(json_str)
    resp.content_type='application/json'
    return resp



