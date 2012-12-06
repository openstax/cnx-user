


"""
runtests 
--------

This is a script (not setup as as an entry point, probably needs to be)
to execute tests in :rf:`rhaptos2.user`

useage:

Run all tests with the given config

   python runtests.py --config=../../../local.ini 

Run only the test modules in modules

   python runtests.py --config=../../../local.ini 

Prepopulate (does not build tables)

   python runtests.py --config=../../../local.ini --prepopulate=Y

this version will connect to the DB in local.ini, and (assuming the tables exist)
will insert through psycopg2 five test users. 

(OK I swapped out the sqlalchemy prepopulation (which creates tables too) so the whole 
table creation thing is a little awkward and needs fixing)

.. todo:: fix table creation in prepopulation



"""


import os
import psycopg2
from nose import with_setup
import json
import nose

from rhaptos2.user import backend, usermodel
from rhaptos2.user.backend import db_session

#######

def get_config(confpath):

    HERE = os.path.abspath(os.path.dirname(__file__))
    CONFD_PATH = os.path.join(HERE, confpath)
    from rhaptos2.common.configuration import (
        find_configuration_file,
        Configuration,
        )
    config = Configuration.from_file(CONFD_PATH)
    backend.initdb(config)  
    return config




def prepopulate(settings):
    """
    :warn: Horrible hack

    Annoyance: The Configuration object from pumazi (as is convention)
               turns ini section "[app]" into the root of the object/dict
               However nosetest_config does NOT.
               So, I end up with two config dicts 
               - normal: one with [app] in the current namespace and all sections one lower
               - nosetest_config - straight ini sections-> levels in dict.
               I can either fiddle with normal dict here and add in a [app] dict level
               or frig the .ini file

    This is just a horrible hack.
    """
    import setupfortests
    appkeys = [i for i in foo if i != "globals"]
    d = {'app':{}}
    for k in appkeys:
        d['app'][k] = settings[k]

    setupfortests.config = d 
    setupfortests.setup()
    setupfortests.teardown()


if __name__ == "__main__":
    from optparse import OptionParser
    usage = "runtests.py --config=../../../local.ini"
    parser = OptionParser(usage=usage)
    parser.add_option("--config", action='store', dest='config',
                      )
    parser.add_option("--prepopulate", action='store', dest='prepopulate',
                      )
    parser.add_option("--tests", action='store', dest='tests',
                      )
    parser.add_option("--match", action='store', dest='match',
                      help="give a regex to match tests - usually just give (uniq) test name. DO not mix with --tests")

    opts, args = parser.parse_args()
    config = get_config(opts.config)

    ### Seems nice to reuse testing rig for prepopulation
    if opts.prepopulate:

        prepopulate(config)

    else:

        argvlist = ['nosetests',
                    '--tc-file=%s' % opts.config, 
                    '-vv']
        #this is very weak - no testing this is valid CSV list 

        if opts.tests: argvlist.append('--tests=%s' % opts.tests)
        if opts.match: argvlist.append('--match=%s' % opts.match)


        nose.run(argv=argvlist)
