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
from urllib import urlencode
from urlparse import urlparse, urlunparse

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
from sqlalchemy import or_
from sqlalchemy.exc import DBAPIError
from velruse.events import AfterLogin

from .interfaces import ILoginDataExtractor, IActiveIdentityProviders
from .utils import diffdict, discover_uid
from .models import (
    DBSession, User, Identity,
    user_schema,
    )


logger = logging.getLogger('cnxauth')
here = os.path.abspath(os.path.dirname(__file__))
REFERRER_SESSION_KEY = 'referrer_info'


@view_config(route_name='index')
@view_config(route_name='catch-all')
def index(request):
    index_html = request.registry.settings['~index.html']
    with open(index_html, 'r') as f:
        return render_to_response('string', f.read())


@view_config(route_name='identity-providers', renderer='json')
def identity_providers(request):
    """Produces a data structure of identity providers."""
    return request.registry.getUtility(IActiveIdentityProviders)


@view_config(route_name='get-users', request_method='GET', renderer='json')
def get_users(request):
    limit = request.params.get('limit', 10)
    offset = request.params.get('page', 0) * limit
    query = request.params.get('q', None)
    is_a_query = query is not None
    _tokenizer = lambda q: [t for t in q.split() if t]

    if is_a_query:
        user_query = DBSession.query(User)
        criteria = []
        for term in _tokenizer(query):
            term_set = (User.firstname.like('%{}%'.format(term)),
                        User.surname.like('%{}%'.format(term)),
                        User.email==term,
                        )
            criteria.extend(term_set)
        user_query = user_query.filter(or_(*criteria))
        try:
            users = user_query.order_by(User.surname) \
                .limit(limit).offset(offset) \
                .all()
        except DBAPIError:
            raise httpexceptions.HTTPServiceUnavailable(
                    connection_error_message,
                    content_type='text/plain',
                    )
    else:
        try:
            users = DBSession.query(User) \
                .order_by(User.surname) \
                .limit(limit).offset(offset) \
                .all()
        except DBAPIError:
            raise httpexceptions.HTTPServiceUnavailable(
                    connection_error_message,
                    content_type='text/plain',
                    )
    return users


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

    permissible = security.has_permission('view', user, request)
    if not permissible:
        raise httpexceptions.HTTPForbidden()
    return user


@view_config(route_name='put-user', request_method=('PUT', 'PATCH',),
             renderer='json')
def put_user(request):
    user = get_user(request)

    # Does the user have write access?
    permissible = security.has_permission('edit', user, request)
    if not permissible:
        raise httpexceptions.HTTPForbidden()

    # Update the user data.
    current_data = user_schema.dictify(user)
    posted_data = user_schema.deserialize(request.json)
    differences = diffdict(current_data, posted_data)
    for key, value in differences.iteritems():
        setattr(user, key, value)
    return user


@view_config(route_name='get-user-identities', request_method='GET',
             renderer='json')
def get_user_identities(request):
    user = get_user(request)
    # Since we are utilizing the another view to acquire the user object,
    #   that view does permissions checking and will prevent any
    #   unauthorized usage from moving forward.
    return user.identities


@view_config(route_name='delete-user-identity', request_method='DELETE')
def delete_user_identity(request):
    # Grab the identity
    id = request.matchdict['identity_id']
    try:
        identity = DBSession.query(Identity) \
            .filter(Identity.id==id) \
            .first()
    except DBAPIError:
        raise httpexceptions.HTTPServiceUnavailable(connection_error_message,
                                                    content_type='text/plain',
                                                    )
    if identity is None:
        raise httpexceptions.HTTPNotFound()
    elif len(identity.user.identities) <= 1:
        raise httpexceptions.HTTPForbidden("Cannot delete the only remaining "
                                           "identity connection.")
    # Check that this user has permission to remove an identity.
    permissible = security.has_permission('delete', identity, request)
    if not permissible:
        raise httpexceptions.HTTPUnauthorized()

    # Remove the identity
    DBSession.delete(identity)
    raise httpexceptions.HTTPNoContent()


def get_token_store():
    """Retrieve the key store for the service exchange tokens."""
    registry = get_current_registry()
    # FIXME The keystore is hardcoded against our existing sqla url.
    #       This should be a settings based connection utility lookup.
    sqla_url = registry.settings['sqlalchemy.url']
    token_storage = anykeystore.create_store('sqla', url=sqla_url)
    return token_storage


@subscriber(AfterLogin)
def capture_requesting_service(event_or_request):
    if isinstance(event_or_request, AfterLogin):
        # 'tis and event
        request = event_or_request.request
    else:
        request = event_or_request
    settings = request.registry.settings

    # We may have already captured the referrer information...
    if REFERRER_SESSION_KEY in request.session:
        return

    def parse_service_url(url):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        if netloc.find(':') >= 1:  # smalled possible, one char
            domain, port = netloc.split(':')
        else:
            domain = netloc
            port = parsed_url.scheme == 'http' and 80 or 443
        return domain, int(port)

    # Capture the referrer either through the login POST data
    #   or via the HTTP_REFERER environment variable.
    came_from = request.params.get('came_from', None)
    if came_from is not None:
        service_domain, service_port = parse_service_url(came_from)
    elif request.referrer is not None:
        came_from = request.referrer
        service_domain, service_port = parse_service_url(came_from)
    else:
        # Note, the following 'referer' is not miss-spelled.
        raise httpexceptions.HTTPBadRequest("Missing HTTP Referer")

    # Are local services enabled? This allows services running in the same
    #   address space to look remote.
    local_services_enabled = settings.get('allow-local-services', False)
    # Compare the referrer with the server host to see if they
    #   are the same. If they are, then we do not capture the referrer
    #   information, except when the 'allow-local-service' setting
    #   has been enabled.
    server_addr = socket.gethostbyname(request.server_name)
    referrer_addr = socket.gethostbyname(service_domain)
    is_not_local_request = server_addr != referrer_addr
    if is_not_local_request or local_services_enabled:
        # TODO Clean this up in the denied login view, which at this point
        #      does not exist.
        request.session[REFERRER_SESSION_KEY] = {
            'domain': service_domain,
            'port': service_port,
            'came_from': came_from,
            }
    # Note, this is an event subscriber, therefore nothing is directly
    #   returned.


@view_config(route_name='server-login', request_method=['GET', 'POST'])
def lazy_login(request):
    """Provide a login interface for those services not wanting to do
    the login logic in their application interface. It's important to
    direct traffic to this route because it captures necessary information
    that would otherwise be acquired via other api pieces."""
    # Capture the requesting service info.
    capture_requesting_service(request)

    # Is the user already authenticated?
    user_id = authenticated_userid(request)
    if user_id is not None:
        raise _login(request, user_id)

    # Forward the user to the web interface.
    raise httpexceptions.HTTPFound(location=request.route_url('www-login'))


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

def _login(request, user_or_id):
    """Given the request and user login and procedure to the valid location."""
    if isinstance(user_or_id, User):
        user_id = str(user_or_id.id)
    else:
        user_id = user_or_id
    # Remember the authenticated user for future requests.
    auth_headers = remember(request, user_id)

    # Check the session for endpoint redirection otherwise pop the
    #   user over to their user profile /user/{id}
    if REFERRER_SESSION_KEY in request.session:
        token = str(uuid.uuid4())
        store = get_token_store()
        value = user_id
        store.store(token, value)  # XXX Never expires.
        # Send the user back to the service with the token and
        #   information about where they came from.
        referrer_info = request.session.get(REFERRER_SESSION_KEY)
        location = generate_service_validation_url(referrer_info, token)
        # Cleanup the referrer info now that it's no longer useful.
        del request.session[REFERRER_SESSION_KEY]
    else:
        location = request.route_url('www-get-user', id=user_id)
    return httpexceptions.HTTPFound(location=location, headers=auth_headers)


@view_config(context='velruse.AuthenticationComplete')
def login_complete(request):
    """This view is hit after a visitor has successfully authenticated with
    one of the registered identity providers.

    The successfully authenticated visitor will be remembered (given a cookie)
    and redirected either to their profile page or back to the remote service
    the came from. See ``capture_requesting_service`` for details on the
    information put into a remote service redirect.
    """
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
        data_extractor = request.registry.queryMultiAdapter(
                (user, identity), ILoginDataExtractor, name=identity.name)
        if data_extractor:
            data_extractor()
        DBSession.add(user)
    except DBAPIError:
        raise httpexceptions.HTTPServiceUnavailable(connection_error_message,
                                                    content_type='text/plain',
                                                    )
    return _login(request, user)

def generate_service_validation_url(referrer_info, token):
    query_str = urlencode(dict(token=token, next=referrer_info['came_from']))
    url_parts = ['https', referrer_info['domain'], '/valid', '', query_str, '']
    if get_current_registry().settings.get('allow-local-services', False):
        url_parts[0] = 'http'
        url_parts[1] = '{}:{}'.format(referrer_info['domain'],
                                      referrer_info['port'])
    location = urlunparse(url_parts)
    return location


@view_config(route_name='server-check', request_method=['GET', 'POST'],
             renderer='json')
def check(request):
    """Check the token given to the external service by the user is
    a valid token."""
    # Pull the token out of the request.
    token = request.params['token']
    store = get_token_store()

    try:
        # FYI token expiration of the token/key is checked on retrieval.
        user_id = store.retrieve(token)
    except KeyError:
        raise httpexceptions.HTTPBadRequest("Invalid Token")
    except:
        raise httpexceptions.HTTPInternalServerError("Problem connecting to "
                                                     "the token storage.")
    return {'id': str(user_id),  # uuid.UUID to str for JSON rendering.
            'url': request.route_url('get-user', user_id=user_id),
            }

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
