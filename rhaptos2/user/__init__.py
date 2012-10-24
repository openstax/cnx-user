#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


"""
initialise the Flask app here. 



"""

from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort


import datetime
import datetime
import md5, random
import os, sys
import flask
import statsd
import json
from functools import wraps
import logging
import uuid
from rhaptos2.common import conf, log, err


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
    
    app.logger.log(goodlvl, msg, extra=extra)         
    
    

def set_logger(apptype, app_configd):
    """
    useage:
        lg.warn("Help", extra={'statsd':['rhaptos2.repo.module', 
                                         'bamboo.foo.bar']})

    """
    lg = logging.getLogger(apptype)

    ### Trapping basic missing conf
    uselogging = "%s_use_logging" % apptype
    loglevel = "%s_loglevel" % apptype

    if uselogging not in confd.keys():
        confd[uselogging] = 'Y'

    if loglevel not in confd.keys():
        confd[loglevel] = 'DEBUG'
    ###

    ## define handlers
    hdlr2 = log.StatsdHandler(app.config['bamboo_statsd_host'],
                    int(app.config['bamboo_statsd_port']))

    hdlr = logging.StreamHandler()

    ## formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s  - %(request_id)s - %(user_id)s - %(message)s')

    hdlr.setFormatter(formatter)
    #hdlr2 just sends statsd calls so does not need formatter ...

    app.logger.addHandler(hdlr)
    app.logger.addHandler(hdlr2)

    app.logger.setLevel(confd[loglevel])

    ##done.


def get_version():
    '''Making very broad assumptions about the existence of files '''
    d = os.path.dirname(__file__)
    try:
        v = open(os.path.join(d, 'version.txt')).read().strip()
        return v
    except Exception, e:
        return '0.0.0'
    #todo: think about this 


apptype = 'rhaptos2user'
confd = conf.get_config(apptype)
app = Flask(__name__)
app.config.update(confd)

#set_logger(apptype, app.config)

@app.before_request
def requestid():
    g.requestid = uuid.uuid4()
    g.request_id = g.requestid

import rhaptos2.user.views
