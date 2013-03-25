#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


'''
setup.py for rhaptos2

'''

from setuptools import setup, find_packages
import os, glob

def get_version():
    """ return a version number, or error string.

    We are assuming a file version.txt always exists. By convention
    populate that file with output of git describe
    """

    try:
        v = open("version.txt").read().strip()
    except:
        v = "UNABLE_TO_FIND_RELEASE_VERSION_FILE"
    return v


setup(name='rhaptos2.user',
      version=get_version(),
      author='See AUTHORS.txt',
      author_email='info@cnx.org',
      url='https://github.com/Connexions/rhaptos2.user',
      license='LICENSE.txt',
      description='User functions for rhaptos2',
      packages=find_packages(),
      namespace_packages=['rhaptos2'],
      install_requires=[
          "flask >= 0.8",
          "statsd",
          "requests",
          "pylint",
          "python-memcached",
          "nose",
          "rhaptos2.common",
          "SQLAlchemy",
          "unittest-xml-reporting",
          "psycopg2",
          ],
      package_data={'rhaptos2.user': ['templates/*.*',
                                      'static/*.*',
                                      'tests/*.*'],
                    },
      entry_points = """\
[console_scripts]
run_rhaptos2user.py = rhaptos2.user.run:main
"""
      )

