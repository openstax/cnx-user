
=============
Rhaptos2 User
=============

Rhaptos2 User is a database that provides a REST-ful API to query open
identifiers (OpenID, Mozilla Persona) and retrieve back the fuill
details of a user within our system.


Outline
-------

We have a postgresql database, with two tables (cnxuser and cnxidentifier)
cnxidentifier is the external thridparty identifier of our users (either openid
or persona).  We store their identifier linked to their user details in cnxuser.

The web server is a simple Flask server, that is run from run.py.
Config is a .ini file. and the std developer version is in package root.
Tests are in tests/ and expected to be run via runtests.py which then passes
config details onto nosetest.

It is expected to run the server from within a virtualenv - this can be setup
usiong the requirements.txt file in package root and then :command:`setup.py develop`
on the src of rhaptos2.user and rhaptos2.common.

A script to do the above is in :ref:`bamboo.scaffold.scripts`


Contents:

.. toctree::
   :maxdepth: 1
   :glob:
   
   *  


Draft Specification:

   
.. toctree::
   :maxdepth: 1

   spec/index


Related Projects
================

* `rhaptos2.repo <http://frozone.readthedocs.org>`_
* `rhaptos2.user <http://rhaptos2user.readthedocs.org>`_
