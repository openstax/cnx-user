import os, glob
from setuptools import setup, find_packages


install_requires = (
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
    )

setup(
    name='cnx-auth',
    version='0.1',
    author='Connexions team',
    author_email='info@cnx.org',
    url="https://github.com/pumazi/cnx-auth",
    license='LICENSE.txt',
    description="Authentication services for the Connexions components",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points="""\
    [paste.app_factory]
    main = cnxauth:main
    [console_scripts]
    initialize_cnx-auth_db = cnxauth.scripts.initializedb:main
    """,
    )
