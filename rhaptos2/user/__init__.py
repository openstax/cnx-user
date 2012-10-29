# -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


"""__init__.py (rhaptos.repo) - Rhaptos application package

Author: Paul Brian
(C) 2012 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import os
import sys
import datetime
import md5
import random
import statsd
import json
import logging
import uuid
import flask  # XXX Why is this imported twice (see 2 lines down)?
from functools import wraps

from flask import (
    Flask, render_template,
    request, g, session, flash,
    redirect, url_for, abort,
    )

from rhaptos2.common import conf, log, err

import pkg_resources  # part of setuptools
__version__ = pkg_resources.require("rhaptos2.user")[0].version

APPTYPE = 'rhaptos2user'
VERSION = __version__
_app = None


"""
Instantiation 

Now using a "appfactory" - sanity from pumazi

  from rhaptos2.user import set_app
  confd = rhaptos2.common.conf.get_config(["rhaptos2user", "bamboo"])
  _app = Flask("rhaptos2.user")
  set_app(_app, confd)

  ###now global _app in __init__ is a Flask app
  ### then app = get_app() in any module will
  ### put it into glboal module namespave for ease each time


"""



def get_app():
    """Get the application object"""
    global _app
    return _app

def set_app(app, _confd={}):
    """Set the global application object

    """
    global _app
    _app = app

    #.. todo:: why not pass confd around all time instead of app.config???
    _app.config.update(_confd)
    hdlrs = set_logger(APPTYPE, _confd)
    for hdlr in hdlrs:
        _app.logger.addHandler(hdlr)

    dolog("DEBUG", "test")

    #allow views to use the app in decorators
    import rhaptos2.user.views

    return _app



def dolog(lvl, msg, caller=None, statsd=None):
    """wrapper function purely for adding context to log stmts

    I am trying to keep this simple, no parsing of the stack etc.

    caller is the function passed when the dolog func is called.  We jsut grab its name
    extras is likely to hold a list of strings that are the buckets


    >>> dolog("ERROR", "whoops", os.path.isdir, ['a.b.c',])


    """


    lvls = {
    "CRITICAL" : 50,
    "ERROR"    : 40,
    "WARNING"  : 30,
    "INFO"     : 20,
    "DEBUG"    : 10,
    "NOTSET"   : 0
    }
    try:
        goodlvl = lvls[lvl]
    except:
        goodlvl = 20 ###!!!

    #create an extras dict, that holds curreent user, request and action notes
    if caller:
        calledby = "rhaptos2.loggedin." + str(caller.__name__)
    else:
        calledby = "rhaptos2.loggedin.unknown"

    if statsd:
        statsd.append(calledby)
    else:
        statsd = [calledby,]

    try:
        request_id = g.request_id
    except:
        request_id = "no_request_id"

    try:
        user_id = g.user_id
    except:
        user_id = "no_user_id"

    extra = {'statsd': statsd,
             'user_id': user_id,
             'request_id': request_id}


    try:
        _app.logger.log(goodlvl, msg, extra=extra)
    except Exception, e:
        print extra, msg, e

def set_logger(apptype, _confd):
    """

    useage:
        lg.warn("Help", extra={'statsd':['rhaptos2.repo.module',
                                         'bamboo.foo.bar']})

    """


    ## define handlers
    stats_hdlr = log.StatsdHandler(_confd['rhaptos2user_statsd_host'],
                    int(_confd['rhaptos2user_statsd_port']))

    stream_hdlr = logging.StreamHandler()

    ## formatters - reduced this as bug #39 prevents extra being used. 
#    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s  - %(request_id)s - %(user_id)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s  - %(message)s')

    stream_hdlr.setFormatter(formatter)
    stats_hdlr.setFormatter(formatter)

    return (stream_hdlr, stats_hdlr)










