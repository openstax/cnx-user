#!/usr/bin/env python
#! -*- coding: utf-8 -*-


""" setup.py - rhaptos2.user

Author: Paul Brian
(C) 2012 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from setuptools import setup, find_packages
import os, glob
from bamboo.setuptools_version import versionlib


setup(
    name='rhaptos2.user',
    version=versionlib.get_version('.'),
    packages=find_packages(),
    namespace_packages=['rhaptos2'],
    author='See AUTHORS.txt',
    author_email='info@cnx.org',
    url='https://github.com/Connexions/rhaptos2.user',
    license='LICENSE.txt',
    description="New editor / repo / system for cnx.org " \
                "-rhaptos2.readthedocs.org",
    install_requires=[
        "bamboo.setuptools_version", 
        "flask >= 0.9",
        "statsd",
        "requests",
        "nose",
        "rhaptos2.common",
        "unittest-xml-reporting",
        ##"mikado.oss.doctest_additions",
        ],
    include_package_data=True,
    package_data={'rhaptos2.repo': ['templates/*.*',
                                    'static/*.*',
                                    'tests/*.*'],
                  '':['RELEASE_VERSION',] 
                  },
    entry_points = """\
[console_scripts]
start_rhaptos2user = rhaptos2.user.run:main
""",
    )

