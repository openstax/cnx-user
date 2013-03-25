#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
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

from rhaptos2.user import get_app, dolog, usermodel
from rhaptos2.user.backend import db_session

app = get_app()


@app.before_request
def requestid():
    g.requestid = uuid.uuid4()
    g.request_id = g.requestid

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    dolog("INFO", "THis is request %s" % g.requestid)
    return "This is the USer Database for CNX"


@app.route('/openid/', methods=["GET",])
def get_user_by_identifier():
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

    """
    qstr = request.query_string
    unquoted_identifier = qstr.replace("user=", "")
    unquoted_identifier = urllib.unquote(unquoted_identifier)
    dolog("INFO", "I saw identifier: %s" % unquoted_identifier)

    try:
        userobj = usermodel.get_user_by_identifier(unquoted_identifier)
        dolog("INFO", "%s <- userobj from get by identifer" % str(userobj))
    except err.Rhaptos2Error, e:
        abort(404)

    resp = flask.make_response(userobj.jsonify())
    resp.content_type='application/json'
    return resp


@app.route('/user/<user_id>', methods=["GET",])
def get_user(user_id):
    """

    """
    try:
        uobj = usermodel.get_user(user_id)
    except err.Rhaptos2Error, e:
        abort(404)

    resp = flask.make_response(uobj.jsonify())
    resp.content_type='application/json'
    return resp


@app.route('/user/', methods=["POST",])
def vw_post_user():
    """ """


    js = request.json
    ### .. todo:: parse incvoming user dict
    dolog("INFO", "***" + repr(js) + str(type(js)))
    u = usermodel.post_user(js)
    return "Saved"


@app.route('/user/<user_id>', methods=["PUT",])
def vw_put_user(user_id):
    """ """
    ###
    #session add etc here
    js = request.json
    dolog("INFO", "***PUT:" + repr(js) + str(type(js)))
    ### .. todo:: parse the posted / putted dict???
    try:
        u = usermodel.put_user(js, user_id)
    except:
        abort(401)#.. todo:: meaningful error messages to user please. Flash?
    return "Saved"

def view_all_users():
    """ """
    ###

    rs = usermodel.get_all_users()
    users = [u.to_dict() for u in rs]
    json_str = json.dumps(users)
    resp = flask.make_response(json_str)
    resp.content_type='application/json'
    return resp

@app.route('/users/', methods=["GET",])
def search_user():
    """
    we support two modes::

       GET /users/
          (returns all users - devel only)
       GET /users/?search=<fragment>
          (uses a general search)

    search will search many fields (currently fullname and email)
    A new search feature willl likely allow

       GET /users/?fullname=<fragment>&email=<fragment2>
          (uses keyvalues as filters)


    """

    qstr = request.query_string
    if qstr.strip() == '':
        #no query, return all
        return view_all_users()

    elif "search" in request.args:
        ###too much hardcoding
        namefrag = request.args['search']

        try:
            matchlist = usermodel.get_user_by_name(namefrag)
            dlist = [u.to_dict() for u in matchlist]
        except err.Rhaptos2Error, e:
            abort(404)

        data = json.dumps(dlist)
        callback = request.args.get('callback', None)
        if callback is None:
            # Send as JSON
            content_type = 'application/json'
        else:
            # Send as JSONP with callback defined by request.
            data = '{0}({1})'.format(callback, data)
            content_type = 'application/javascript'

        resp = flask.make_response(data)
        resp.content_type = content_type
        return resp

    else:
        abort(400) #needs ?search=x syntax

