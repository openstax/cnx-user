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

from rhaptos2.user import app, dolog
#circular reference ? see http://flask.pocoo.org/docs/patterns/packages/




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
    originally this use <idenfitfier> to pluckjt eh id from a path.
    However if I sent in an openid id, with / in it, even quoted, Falsk would
    pre-unquote and try to route the url now with added slashes.

    I switched to a quick fix - now passing in a quote_plus'd query string named user
    
    /user?user=foo

    ##Write tests!
    """
    qstr = request.query_string
    
    #    unquoted_identifier = urllib.unquote(identifier)
    unquoted_identifier = qstr.replace("user=", "")

    dolog("INFO", "THis is request %s" % g.requestid)
    dolog("INFO", "I saw identifier: %s" % unquoted_identifier)
    ##actually look up the user here !
    resp = flask.make_response(stubjsondoc)
    resp.content_type='application/json'
    return resp



