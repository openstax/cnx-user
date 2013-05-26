# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import logging
import json

import velruse
from pyramid import httpexceptions
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid, remember
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .utils import discover_uid
from .models import DBSession, User, Identity
from . import usermodel


logger = logging.getLogger('cnxauth')
here = os.path.abspath(os.path.dirname(__file__))


@view_config(route_name='index')
@view_config(route_name='catch-all')
def index(request):
    with open(os.path.join(here, 'assets', 'index.html'), 'r') as f:
        return render_to_response('string', f.read())

@view_config(route_name='identity-providers', renderer='json')
def identity_providers(request):
    """Produces a data structure of identity providers."""
    providers = [
        # {id: <string>, name: <human-readable-name>,
        #  location: <login-url>,
        #  # optionally...
        #  fields: {name: <name>, type: (text|hidden),
        #           # necessary for hidden fields
        #           value: <default-value>,
        #           # useful for text fields
        #           label: <text>,
        #           placeholder: <text>,
        #           },
        #  autosubmit: (True|False),
        #  },
        {'id': 'openid', 'name': 'OpenID',
         'location': velruse.login_url(request, 'openid'),
         'fields': [{'type': 'text', 'name': 'openid_identifier',
                     'label': "OpenID identifier string",
                     'placeholder': 'http://me.example.com',
                     },
                    ],
         'auto_submit': False,
         },
        {'id': 'google', 'name': 'Google',
         'location': velruse.login_url(request, 'google'),
         'auto_submit': True,
         },
        ]
    return providers


def acquire_user(request):
    """Retrieve the user from the request or make one."""
    user_id = authenticated_userid(request)
    if user_id is not None:
        user = DBSession.query(User) \
            .filter(User.id==user_id) \
            .one()
    else:
        user = User()
        DBSession.add(user)
    return user


@view_config(context='velruse.AuthenticationComplete')
def login_complete(request):
    context = request.context
    identifier = discover_uid(context)

    # Create user and identity entries if none are found.
    try:
        identity = DBSession.query(Identity) \
            .filter(Identity.identifier==identifier) \
            .filter(Identity.name==context.provider_name) \
            .filter(Identity.type==context.provider_type) \
            .first()
        if not identity:
            # So we have a new identity and potentially a new user, but
            #   that is unknown at this time.
            user = acquire_user(request)
            if user.id is None:
                # We need the user id to make the relationship.
                DBSession.flush()
            identity = Identity(identifier,
                                context.provider_name, context.provider_type,
                                json.dumps(context.profile),
                                json.dumps(context.credentials),
                                user=user)
            DBSession.add(identity)
        user = identity.user
    except DBAPIError:
        raise httpexceptions.HTTPServiceUnavailable(connection_error_message,
                                                    content_type='text/plain',
                                                    )
    # Remember the authenticated user for future requests.
    auth_headers = remember(request, user.id)

    # TODO Check the session for endpoint redirection otherwise pop the
    #      user over to their user profile /user/{id}
    location = request.route_url('www-get-user', id=user.id)
    return httpexceptions.HTTPFound(location=location, headers=auth_headers)


@view_config(route_name='get-user', request_method='GET', renderer='json')
def get_user(request):
    id = request.matchdict['user_id']
    try:
        user = DBSession.query(User).filter(User.id==id).first()
    except DBAPIError:
        raise httpexceptions.HTTPServiceUnavailable(connection_error_message,
                                                    content_type='text/plain',
                                                    )
    if user is None:
        raise httpexceptions.HTTPNotFound()
    return user


@view_config(route_name='get-user-identities', request_method='GET',
             renderer='json')
def get_user_identities(request):
    user = get_user(request)
    return user.identities


connection_error_message = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_{{project}}_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
