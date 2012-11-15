#!/usr/bin/env python
# -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###
"""Launch the repo app.

Author: Paul Brian, Michael Mulich
Copyright (c) 2012 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from rhaptos2.common import runner
from rhaptos2.user import make_app


def main():
    """Run the application, to be used to start up one instance"""
    runner.main(make_app)


if __name__ == '__main__':
    main()

