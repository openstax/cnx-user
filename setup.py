import os, glob
from setuptools import setup, find_packages


install_requires = (
    "requests",
    "SQLAlchemy",
    "psycopg2",
    )

setup(
    name='cnx-auth',
    version='0.1',
    author='Connexions team',
    author_email='info@cnx.org',
    url='https://github.com/pumazi/cnx-auth',
    license='LICENSE.txt',
    description='Authentication services for the Connexions components',
    packages=find_packages(),
    install_requires=install_requires,
    )
