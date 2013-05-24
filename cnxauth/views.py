# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.exceptions import NotFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

import velruse
from . import usermodel


logger = logging.getLogger('cnxauth')
here = os.path.abspath(os.path.dirname(__file__))

@view_config(route_name='index')
@view_config(route_name='catchall')
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


@view_config(context='velruse.AuthenticationComplete', renderer='json')
def login_complete(request):
    context = request.context
    # Create user and identity entries if none are found.

    # Check the session for endpoint redirection otherwise pop the
    #   user over to their user profile /user/{id}

    # XXX Developer debug output
    result = {
        'provider_type': context.provider_type,
        'provider_name': context.provider_name,
        'profile': context.profile,
        'credentials': context.credentials,
        }
    return result


@view_config(route_name='get-user', request_method='GET', renderer='json')
def get_user(request):
    id = request.multidict['id']
    try:
        user = usermodel.get_user(id)
    except usermodel.Rhaptos2Error, e:
        raise NotFound()
    return {'id': user.id, 'fullname': user.fullname, 'email': user.email}


@view_config(route_name='post-user', request_method=['POST', 'PUT'])
def post_user(request):
    id = request.multidict.get('id', None)
    data = request.json_body
    if request.method == 'PUT' and id is None:
        raise HttpBadRequest("PUT without an ID")
    elif request.metho == 'POST':
        user = usermodel.post_user(data)
    else:
        user = usermodel.put_user(data, id)
    return "Saved"


@view_config(route_name='query', request_method='GET', renderer='json')
def query(request):
    q = request.query_string.get('q', '')
    try:
        matchlist = usermodel.get_user_by_name(q)
    except usermodel.Rhaptos2Error, e:
        raise HTTPInternalServerError()
    return [u.id for u in matchlist]
