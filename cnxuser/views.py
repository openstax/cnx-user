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
import socket
import uuid
from urlparse import urlparse

import anykeystore
import velruse
from pyramid import security
from pyramid import httpexceptions
from pyramid.events import subscriber
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid, remember
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from velruse.events import AfterLogin

from .utils import discover_uid
from .models import DBSession, User, Identity
from ._velruse import IActiveIdentityProviders


logger = logging.getLogger('cnxauth')
here = os.path.abspath(os.path.dirname(__file__))
REFERRER_SESSION_KEY = 'referrer_info'


@view_config(route_name='index')
@view_config(route_name='catch-all')
def index(request):
    with open(os.path.join(here, 'assets', 'index.html'), 'r') as f:
        return render_to_response('string', f.read())

@view_config(route_name='identity-providers', renderer='json')
def identity_providers(request):
    """Produces a data structure of identity providers."""
    return request.registry.getUtility(IActiveIdentityProviders)


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

    permissable = security.has_permission('view', user, request)
    if not isinstance(permissable, security.Allowed):
        raise httpexceptions.HTTPForbidden()
    return user


@view_config(route_name='get-user-identities', request_method='GET',
             renderer='json')
def get_user_identities(request):
    user = get_user(request)
    # Since we are utilizing the another view to acquire the user object,
    #   that view does permissions checking and will prevent any
    #   unauthorized usage from moving forward.
    return user.identities


def get_token_store():
    """Retrieve the key store for the service exchange tokens."""
    registry = get_current_registry()
    # FIXME The keystore is hardcoded against our existing sqla url.
    #       This should be a settings based connection utility lookup.
    sqla_url = registry.settings['sqlalchemy.url']
    token_storage = anykeystore.create_store('sqla', url=sqla_url)
    return token_storage


@subscriber(AfterLogin)
def capture_requesting_service(event):
    request = event.request

    def parse_service_domain(url):
        netloc = urlparse(event.request.referrer).netloc
        return netloc.split(':', 1)[0]

    # Capture the referrer either through the login POST data
    #   or via the HTTP_REFERER environment variable.
    came_from = request.params.get('came_from', None)
    if came_from is not None:
        service_domain = parse_service_domain(came_from)
    elif request.referrer is not None:
        came_from = request.referrer
        service_domain = parse_service_domain(came_from)
    else:
        # Note, the following 'referer' is not miss-spelled.
        raise HTTPServiceUnavailable("Missing HTTP Referer")

    server_addr = socket.gethostbyname(request.server_name)
    referrer_addr = socket.gethostbyname(service_domain)

    # Compare the referrer with the server host to see if they
    #   are the same. If they are, then we do not capture the referrer
    #   information, which would otherwise to used later by the login
    #   completion view to supply a token for the remote service.
    is_not_local_request = server_addr != referrer_addr
    if is_not_local_request:
        # TODO Clean this up in the denied login view, which at this point
        #      does not exist.
        request.session[REFERRER_SESSION_KEY] = {
            'domain': service_domain,
            'came_from': came_from,
            }


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
    auth_headers = remember(request, str(user.id))

    # Check the session for endpoint redirection otherwise pop the
    #   user over to their user profile /user/{id}
    referrer_info = request.session.get(REFERRER_SESSION_KEY)
    if referrer_info is not None:
        token = str(uuid.uuid4())
        store = get_token_store()
        value = "{}%{}".format(user.id, referrer_info['domain'])
        store.store(token, value)  # XXX Never expires.
        location = 'https://{}/valid?token={}'.format(
            referrer_info['domain'], token)
    else:
        location = request.route_url('www-get-user', id=user.id)
    return httpexceptions.HTTPFound(location=location, headers=auth_headers)


@view_config(route_name='server-check', request_method=['GET', 'POST'])
def check(request):
    """Check the token given to the external service by the user is
    a valid token."""
    # Pull the token out of the request.
    token = request.params['token']
    remote = socket.getfqdn(request.remote_addr)
    store = get_token_store()

    try:
        # FYI expiration of the token/key is checked on retrieval.
        value = store.retrieve(token)
        user_id, domain = value.split('%')
        # Check the token was given is valid for the external service domain.
        assert domain == remote
    except:
        raise httpexceptions.HTTPBadRequest("Invalid Token")
    return user_id


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
