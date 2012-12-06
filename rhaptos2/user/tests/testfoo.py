#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


from testconfig import config
from rhaptos2.user.tests.setupfortests import setup, teardown
from nose import with_setup
import sys

@with_setup(setup, teardown)
def test_q():
    """

    I can run the abovewith doctests 
    I can pass config in to doctest
    setup can modufy the conifg

    >>> from testconfig import config
    >>> print config
    {'foo': 'baz'}

    """

    sys.stderr.write(str(config))
    open("/tmp/t", "w").write(str(config))
