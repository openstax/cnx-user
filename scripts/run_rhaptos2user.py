#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


'''
Just launch the main Flask repo app.

'''

from optparse import OptionParser
import os
from rhaptos2.user import app  ## NB repo.__init__ has app as callable...
from rhaptos2.common import conf


def parse_args():

    parser = OptionParser()
    parser.add_option("--host", dest="host",
                      help="hostname to listen on")

    parser.add_option("--port", dest="port",
                      help="port to listen on", type="int")

    parser.add_option("--debug", dest="debug",
                      help="debug on or off.", default=False)


    (options, args) = parser.parse_args()
    return (options, args)

def main():
    '''run the main Flask application, to be used to start up one instance

    
    '''
    opts, args = parse_args()
    #todo: Some validation here??

    s = '########### ENV VARS WE START UP WITH HERE\n'
    for k in os.environ: s += '\n%s:%s' % (k, os.environ[k])
    s += '\n########### ENV VARS END'
    print s

    app.run(host=opts.host, 
                   port=opts.port, 
                   debug=opts.debug,
                   use_reloader=False 
                   )#do not reload even in debug mode - produces new stray processes that supervisor does not ctl.

    

if __name__ == '__main__':
    main()


