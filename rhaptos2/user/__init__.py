# -*- coding: utf-8 -*-
###
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###
"""Rhaptos user profile web application

The application is initialized using the application factory (`make_app`).

To acquire the application from anywhere in this package or extra packages,
use the `get_app` function.

Author: Paul Brian, Michael Mulich
Copyright (c) 2012 Rice University

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

def get_app():
    """Get the application object"""
    global _app
    return _app

def set_app(app):
    """Set the global application object"""
    global _app
    _app = app
    return _app

def make_app(config):
    """Application factory"""
    app = Flask(__name__)
    app.config.update(config)

    set_up_logging(app)

    # Set the application
    app = set_app(app)

    # Initialize the views
    from rhaptos2.user import views

    return app

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


def set_up_logging(app):
    """Set up the logging within the application.

    useage::
        logger.warn("Help",
                    extra={'statsd': ['rhaptos2.repo.module',
                                      'bamboo.foo.bar']})

    """
    config = app.config

    # Define the logging handlers
    statsd_host = config['globals']['bamboo_global']['statsd_host']
    statsd_port = config['globals']['bamboo_global']['statsd_port']
    statsd_handler = log.StatsdHandler(statsd_host, statsd_port)
    stream_handler = logging.StreamHandler()

    # Define the log formatting. Reduced this as bug #39 prevents
    #   extra being used.
    # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s  "
    #                               "- %(request_id)s - %(user_id)s "
    #                               "- %(message)s")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s  "
                                  "- %(message)s")

    statsd_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Set the handlers on the application.
    for handler in (statsd_handler, stream_handler,):
        app.logger.addHandler(handler)

