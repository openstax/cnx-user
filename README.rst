CNX User Service
================

This is a single sign-on application for the Connexions system. It
provides user profiles, identity management, authentication procedures
and remote autentication services. Authentication requests are proxied
to identity providers (e.g. myOpenID, Google, Yahoo, etc.). This
application is a mapper of identities to local user profiles. We
keep this information to help us:

1. Connect identities to a single user profile.
2. Provide a central place for user profile information, which is used
   the various services for various reasons.
3. Provide a single sign-on system for the suite of Connexions applications.
4. Provides user grouping and organization facilities.


Parts of this appliation are modeled after the `CoSign project
<http://weblogin.org>`_. Specifically, our service authentication
verifification process is similar to `CoSign's workflow
<http://weblogin.org/overview.shtml>`_.


Getting started
---------------

This will require a 'Postgres' install. If you are using the
``development.ini`` configuration file, you'll want to set up a
``cnxuser`` database for user ``cnxuser`` with the password
``cnxuser``.

The application is built in Python and can be installed using the
typical Python distribution installation procedure, as follows::

    $ python setup.py install

*Important*: The application depends on a forked copy of ``velruse``
at `pumazi/velruse #cnx-master
<https://github.com/pumazi/velruse/tree/cnx-master>`_. This fork
provides some bug fixes as well as event hooks and possibly other fixes.

This will install the package and a few application specific
scripts. One of these scripts is used to initialize the database with
the applications schema.
::

    $ initialize_cnx-user_db development.ini

To run the application, supply ``pserve`` (the Pyramid framework's
serve script) with an application configuration file
(``development.ini`` has been supplied with the package).
::

    $ pserve development.ini

You can then surf to the address printed out by the above command.

API
---

``/server/login/{identity-provider-id}`` - (POST)
  Posting to this route will invoke the authentication sequence. Some
  identity providers need additional information. See the
  ``/api/identity-provider`` listing for additional fields to
  post. See ``/api/identity-provider`` for more information.

``/server/login/{identity-provider-id}/callback`` -
  The endpoint the identity provider directs the user to after the
  authentication. This get's the user back to our service with
  authentication information.

``/api/identity-providers`` - (GET)
  A collection/listing of identity providers that can be used for
  authentication purposes.

  The identity information provides you with an id, which you can then
  use to build the ``/server/login/{identity-provider-id}`` route. If
  additional information is required in the post, it will be supplied
  in this information. For example, here is a fictitious identity
  provider's information::

      {'id': 'contagious', 'name': 'Contagious‎',
       'location': '/server/login/contagious',
       'fields': [{'type': 'text', 'name': 'identifier',
                   'label': "Contagious identifier",
                   'placeholder': 'example.com/virus-name',
                   },
                  {'type': 'hidden', 'name': 'method',
                   'value': 'inhalation',
                   }
                  ],
       'auto_submit': False,
       }

``/api/users`` - (GET)
  A collection/listing of all users in the system. This uses a paging
  mechanism so that only partial results become available. (GET only)

``/api/users/{user_id}`` - (GET, PUT, PATCH)
  A specific user represented or posted as JSON data.

``/api/users/{user_id}/identities`` - (GET)
  A collection/listing of connected identities with this user.

``/api/users/{user_id}/identities/{identity_id}`` - (GET, DELETE)
  A specific idenity connected with the user.

``/api/groups`` - (GET) [ *not currently available* ]
  A listing of all groups in the system, but without group membership
  information.

``/api/groups/{group_id}`` - (GET) [ *not currently available* ]
  Information about the group. Same info that is listed in
  ``/api/groups``.

``/api/groups/{group_id}/members`` - (GET, PUT) [ *not currently available* ]
  Group members by id. This does not produce full user models. The
  association must manually be put together using
  ``/api/users/{user_id}``.

``/api/users/{user_id}/groups`` - (GET) [ *not currently available* ]
  A user's group membership as a list of group ids.

Server resources
----------------

``/`` & ``/*subpath`` -
  The index view to the UI. The file for this is in the cnx-user
  package at ``cnxuser/assets/index.html``.

``/scripts``, ``/styles`` & ``templates`` -
  These are static resources for web logic (javascript and
  coffeescript), styles (css and less) and client side templates
  (handlebars). These directories are directly linked to directories
  in the cnx-user package at ``cnxuser/assets/``.

License
-------

This software is subject to the provisions of the GNU Affero General
Public License Version 3.0 (AGPL). See license.txt for details.
Copyright (c) 2013 Rice University
