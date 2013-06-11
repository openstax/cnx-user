import os, glob
from setuptools import setup, find_packages


install_requires = (
    'anykeystore',
    'pyramid',
    'requests',
    'velruse',
    'waitress',
    # SQL integration packages
    'transaction',
    'pyramid_tm',
    'SQLAlchemy',
    'zope.sqlalchemy',
    'psycopg2',
    'colanderalchemy',
    )
description = "Authentication and user profiling services for the " \
              "Connexions system components"

setup(
    name='cnx-user',
    version='0.1',
    author='Connexions team',
    author_email='info@cnx.org',
    url="https://github.com/pumazi/cnx-auth",
    license='LICENSE.txt',
    description=description,
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points="""\
    [paste.app_factory]
    main = cnxuser:main
    [console_scripts]
    initialize_cnx-user_db = cnxuser.scripts.initializedb:main
    """,
    )
