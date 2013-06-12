# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import unittest
import json
import socket
import tempfile
import uuid
from urlparse import parse_qs, urlparse

import transaction
from webob.multidict import MultiDict
from pyramid import testing

from .models import DBSession


here = os.path.abspath(os.path.dirname(__file__))
test_data_directory = os.path.join(here, 'test-data')
with open(os.path.join(test_data_directory, 'idents.json'), 'r') as fp:
    _TEST_IDENTS = json.load(fp)
TEST_OPENID_IDENTS = _TEST_IDENTS['openid']
TEST_GOOGLE_IDENTS = _TEST_IDENTS['google']


def _resolve_test_domain(domain, port=80):
    """Given a domain, resolve it down to it's FQDN and ip address."""
    addrs = socket.getaddrinfo(domain, port)
    addr = addrs[0][4][0]
    fqdn = socket.gethostbyaddr(addr)[0]
    return fqdn, addr


class UidDiscoverTests(unittest.TestCase):
    # Tests the utils.discover_uid function.
    # The data here is a mock of the profile data coming out of a
    #   velruse.AuthenticationComplete object.

    def make_one(self, profile):
        from velruse import AuthenticationComplete
        obj = AuthenticationComplete()
        setattr(obj, 'profile', profile)
        return obj

    def test_w_no_info(self):
        # Case where the function is supplied with little or no data.
        # I can't say this would ever happen, but if it does it will
        #   be ready for it.
        from .utils import discover_uid
        data = self.make_one({"accounts": []})
        with self.assertRaises(ValueError):
            uid = discover_uid(data)

    def test_w_general_info(self):
        from .utils import discover_uid
        expected_uid = 'http://junk.myopenid.com'
        data = self.make_one({"accounts": [{"username": expected_uid,
                                            "domain": "openid.net"}]})
        uid = discover_uid(data)
        self.assertEqual(uid, expected_uid)

    def test_w_double_username(self):
        # Case where more than one username is supplied. We should take
        #   the first when a prefered username option hasn't been specified.
        from .utils import discover_uid
        expected_uid = 'http://junk.myopenid.com'
        data = self.make_one({"accounts": [{"username": expected_uid,
                                          "domain": "openid.net"},
                                         {"username": "not-this-one",
                                          "domain": "example.com"},
                                         ]})
        uid = discover_uid(data)
        self.assertEqual(uid, expected_uid)

    def test_w_preferred_username(self):
        # Case where a preferred username has been supplied.
        from .utils import discover_uid
        expected_uid = 'me@example.com'
        data = self.make_one({"accounts": [{"username": "not-this-one",
                                            "domain": "openid.net"},
                                           {"username": expected_uid,
                                            "domain": "example.com"},
                                           ],
                              "preferredUsername": expected_uid})
        uid = discover_uid(data)
        self.assertEqual(uid, expected_uid)


class ModelRelationshipTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_user_to_ident_rel(self):
        firstname = "Jone"
        lastname = "Hao"
        jone_identifier = "https://jone.openid.example.com"
        hao_identifier = "https://hao.openid.example.com"
        from .models import User, Identity
        with transaction.manager:
            user = User()
            user.firstname = firstname
            user.lastname = lastname
            DBSession.add(user)
            DBSession.flush()
            jone_ident = Identity(jone_identifier, '', '', user=user)
            hao_ident = Identity(hao_identifier, '', '', user=user)
            DBSession.add_all([jone_ident, hao_ident])
        with transaction.manager:
            user = DBSession.query(User) \
                .filter(User.firstname==firstname) \
                .one()
            ident = DBSession.query(Identity) \
                .filter(Identity.identifier==jone_identifier) \
                .one()
            self.assertIn(ident, user.identities)
            ident2 = DBSession.query(Identity) \
                .filter(Identity.identifier==hao_identifier) \
                .one()
            self.assertIn(ident2, user.identities)
            self.assertEqual(ident2.user, user)


class PutUserTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={})
        from sqlalchemy import create_engine
        sql_connect_str = 'sqlite://'
        engine = create_engine(sql_connect_str)
        from .models import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_success(self):
        # Given a good set of data in the request, verify the request
        #   goes through and the model is updated.
        # Create a blank user.
        from .models import User
        with transaction.manager:
            user = User()
            DBSession.add(user)
            DBSession.flush()
            user_id = user.id
        request = testing.DummyRequest()
        request.matchdict = {'user_id': user_id}
        data = request.json = request.json_body = {
            'email': 'me@example.com',
            'firstname': 'Smoo',
            'lastname': 'Smoo',
            }

        from .views import put_user
        with transaction.manager:
            user = put_user(request)

        with transaction.manager:
            user = DBSession.query(User).filter(User.id==user_id).one()
            self.assertEqual(user.email, data['email'])
            fullname = "{} {}".format(data['firstname'], data['lastname'])
            self.assertEqual(user.fullname, fullname)

    def test_invalid(self):
        # Given a set of data that includes bogus data as well as fields
        #   that are immuntable by the user, ignore them.
        # We don't have anything in the schema fields that require
        #   strict validation. So we'll ignore most problems.
        from .models import User
        with transaction.manager:
            user = User()
            DBSession.add(user)
            DBSession.flush()
            user_id = user.id
        request = testing.DummyRequest()
        request.matchdict = {'user_id': user_id}
        data = request.json = request.json_body = {
            'id': "select * from users where id='1234';",
            'email': 'homestar@example.com',  # valid
            'fullname': 'Smoo Smoo',
            }

        from .views import put_user
        with transaction.manager:
            user = put_user(request)
            self.assertEqual(user.id, user_id)
            self.assertEqual(user.fullname, '')

        with transaction.manager:
            user = DBSession.query(User).filter(User.id==user_id).one()
            self.assertEqual(user.email, data['email'])
            self.assertEqual(user.fullname, '')


class IdentityDeletionTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp(settings={})
        from sqlalchemy import create_engine
        sql_connect_str = 'sqlite://'
        engine = create_engine(sql_connect_str)
        from .models import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_success(self):
        # Given a user with two or more connected identies remove one
        #   of the identies at the user's request.
        # Create the user and connected identities.
        from .models import Identity, User
        with transaction.manager:
            # Create the user first...
            user = User()
            DBSession.add(user)
            DBSession.flush()
            user_id = user.id
        # It's easier to do this in two transactions to avoid unrealistic
        #   flushing issues.
        with transaction.manager:
            # ...now create the connected identities.
            identities = []
            for name in ('Hao', 'Jone', 'Suse',):
                identity = Identity(name, name, 'openid')
                identity.user_id = str(user_id)
                identities.append(identity)
            DBSession.add_all(identities)
            DBSession.flush()
            identity_ids = [ident.id for ident in identities]

        request = testing.DummyRequest()
        removed_identity_id = identity_ids[0]
        request.matchdict = {'user_id': user_id,
                             'identity_id': removed_identity_id,
                             }

        from .views import delete_user_identity
        from pyramid.httpexceptions import HTTPNoContent
        with self.assertRaises(HTTPNoContent):
            delete_user_identity(request)
        transaction.commit()

        # Did it really remove the identity?
        with transaction.manager:
            identity = DBSession.query(Identity) \
                .filter(Identity.id==removed_identity_id) \
                .first()
            self.assertEqual(identity, None)

    def test_error_on_no_remaining_identities(self):
        # Given a user with only one connected identity, produce an error
        #   disabling the user from removing the only remaining identity.
        # Note, that the we prevent this from happening server side, but
        #   on the client side the user should be given the option to
        #   completely remove the user account.
        self.fail()


# TODO The parse_service_url function needs testing for:
#      - full domain and port
#      - domain without port


class CaptureRequestingServiceTests(unittest.TestCase):
    # Note, the 'capture_requesting_service' function will
    #   ping the network using the 'socket' library.

    def setUp(self):
        self.config = testing.setUp(settings={})

    def tearDown(self):
        testing.tearDown()

    def _make_request(self):
        request = testing.DummyRequest()
        request.server_name = 'localhost'
        # A normal webob request would have these attributes, but they
        #   may not have a value.
        request.referer = request.referrer = None
        # The session factory normally creates the session for us, but
        #   it is not setup in tests or on a dummy request.
        request.session = {}
        return request

    def _make_event(self, request=None):
        from velruse.events import AfterLogin
        if request is None:
            request = self._make_request()
        event = AfterLogin(request)
        return event

    def test_request_wo_referrer_o_came_from(self):
        # Verify an error is raised with requests containing no
        #   referential data (http referer or came_from post value).
        event = self._make_event()

        from .views import capture_requesting_service
        from pyramid.httpexceptions import HTTPBadRequest
        with self.assertRaises(HTTPBadRequest):
            capture_requesting_service(event)

    def test_local_request_w_referrer(self):
        # Verify that local requests pass through without capturing any
        #   data.
        event = self._make_event()

        # Set the referring party info.
        domain = 'localhost'
        referrer = "http://{}:8080/foo/bar".format(domain)
        event.request.referrer = referrer

        from .views import capture_requesting_service
        capture_requesting_service(event)

        from .views import REFERRER_SESSION_KEY
        self.assertNotIn(REFERRER_SESSION_KEY, event.request.session)

    def test_local_request_w_came_from(self):
        # Verify that local requests pass through without capturing any
        #   data.
        event = self._make_event()

        # Set the referring party info.
        domain = 'localhost'
        referrer = "http://{}:8080/foo/bar".format(domain)
        event.request.POST = event.request.params = {}
        event.request.params['came_from'] = referrer

        from .views import capture_requesting_service
        capture_requesting_service(event)

        from .views import REFERRER_SESSION_KEY
        self.assertNotIn(REFERRER_SESSION_KEY, event.request.session)

    def test_remote_request_w_referer(self):
        # Verify that local requests pass through without capturing any
        #   data.
        event = self._make_event()

        # Set the referring party info.
        domain = 'example.com'
        port = 8080
        referrer = "http://{}:{}/foo/bar".format(domain, port)
        event.request.referrer = referrer

        from .views import capture_requesting_service
        capture_requesting_service(event)

        from .views import REFERRER_SESSION_KEY
        self.assertIn(REFERRER_SESSION_KEY, event.request.session)
        ref_info = event.request.session[REFERRER_SESSION_KEY]
        self.assertEqual(ref_info['came_from'], referrer)
        self.assertEqual(ref_info['domain'], domain)
        self.assertEqual(ref_info['port'], port)

    def test_remote_request_w_came_from(self):
        # Verify that local requests pass through without capturing any
        #   data.
        event = self._make_event()

        # Set the referring party info.
        domain = 'example.com'
        port = 8080
        referrer = "http://{}:{}/foo/bar".format(domain, port)
        event.request.POST = event.request.params = {}
        event.request.params['came_from'] = referrer

        from .views import capture_requesting_service
        capture_requesting_service(event)

        from .views import REFERRER_SESSION_KEY
        self.assertIn(REFERRER_SESSION_KEY, event.request.session)
        ref_info = event.request.session[REFERRER_SESSION_KEY]
        self.assertEqual(ref_info['came_from'], referrer)
        self.assertEqual(ref_info['domain'], domain)
        self.assertEqual(ref_info['port'], port)

    def test_local_request_w_local_service_enabled(self):
        # Verify that local requests pass through without capturing any
        #   data.
        self.config.registry.settings['allow-local-services'] = True
        event = self._make_event()

        # Set the referring party info.
        domain = event.request.server_name = 'localhost'
        port = event.request.server_port = 8080
        referrer = "http://{}:{}/foo/bar".format(domain, port)
        event.request.referrer = referrer

        from .views import capture_requesting_service
        capture_requesting_service(event)

        from .views import REFERRER_SESSION_KEY
        self.assertIn(REFERRER_SESSION_KEY, event.request.session)
        ref_info = event.request.session[REFERRER_SESSION_KEY]
        self.assertEqual(ref_info['came_from'], referrer)
        self.assertEqual(ref_info['domain'], domain)
        self.assertEqual(ref_info['port'], port)


class LoginCompleteTests(unittest.TestCase):
    # These tests assume the visitor has come to this service without any
    #   previous session information (unauthentication).

    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        sql_connect_str = 'sqlite://'
        engine = create_engine(sql_connect_str)
        from .models import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        # Initialize the routes required by the view to generate
        #   followup urls.
        from . import register_www_iface
        register_www_iface(self.config)
        # The token store needs access to our sql-url at runtime.
        self.config.registry.settings['sqlalchemy.url'] = sql_connect_str

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def _make_request(self):
        request = testing.DummyRequest()
        request.server_name = 'localhost'
        request.server_port = 8080
        request.session = {}
        return request

    def _make_user(self):
        """Creates a user entry in the database."""
        from .models import User
        with transaction.manager:
            user = User()
            DBSession.add(user)
            DBSession.flush()
            user_id = user.id
        return user_id

    def _make_identity(self, identifier=None, ident=TEST_OPENID_IDENTS[0],
                       user_id=None):
        """Creates an identity and user entry in the database."""
        if identifier is None:
            # Attempt to grab it from the 'ident' value, but this isn't
            #   foolproof.
            try:
                identifier = ident['profile']['accounts'][0]['username']
            except:
                raise RuntimeError("Yeah, you're going to need to be "
                                   "more specific.")
        if user_id is None:
            user_id = self._make_user()

        from .models import Identity
        with transaction.manager:
            identity = Identity(identifier,
                                ident['provider_name'],
                                ident['provider_type'],
                                json.dumps(ident['profile']),
                                json.dumps(ident['credentials']),
                                )
            identity.user_id = user_id
            DBSession.add(identity)
            DBSession.flush()
            identity_id = identity.id

        return identity_id, user_id

    def _make_one(self, ident=TEST_OPENID_IDENTS[0], request=None):
        """Makes a contextual post login request."""
        # Create the request context.
        from velruse import AuthenticationComplete
        if request is None:
            request = self._make_request()
        request.context = AuthenticationComplete(**ident)
        return request

    def test_local_login_w_new_identity(self):
        # Case for a completely new visitor logging into cnx-user locally.
        request = self._make_one()

        from .views import login_complete
        with transaction.manager:
            resp = login_complete(request)

        # Since this is the first visitor and the database is empty,
        #   the new user and identity are the only entries.
        from .models import User, Identity
        user = DBSession.query(User).first()
        identity = user.identities[0]
        self.assertEqual('http://michaelmulich.myopenid.com/',
                         identity.identifier)
        self.assertEqual(302, resp.status_int)
        self.assertEqual(request.route_url('www-get-user', id=user.id),
                         resp.location)

    def test_local_login_w_existing_identity(self):
        # Case where the identity exists, therefore the user exists. This
        #   is a case of reauthentication.
        identifier = "http://philschatz.myopenid.com/"
        identity_id, user_id = self._make_identity(
            identifier, TEST_OPENID_IDENTS[1])
        request = self._make_one(TEST_OPENID_IDENTS[1])

        from .views import login_complete
        with transaction.manager:
            resp = login_complete(request)

        # Since this is the first visitor and the database is empty,
        #   the new user and identity are the only entries.
        from .models import User, Identity
        user = DBSession.query(User).first()
        identity = user.identities[0]
        self.assertEqual(identity.identifier, identifier)
        self.assertEqual(resp.status_int, 302)
        self.assertEqual(resp.location,
                         request.route_url('www-get-user', id=user.id))

    def test_remote_login_w_new_identity(self):
        # Case for a completely new visitor logging into a remote service
        #   that is using cnx-user.
        request = self._make_one()
        domain = 'example.com'
        port = 8080
        came_from = "http://{}:{}/foo/bar".format(domain, port)
        from .views import REFERRER_SESSION_KEY
        request.session[REFERRER_SESSION_KEY] = {
            'domain': domain,
            'port': port,
            'came_from': came_from,
            }

        from .views import login_complete
        with transaction.manager:
            resp = login_complete(request)

        # Since this is the first visitor and the database is empty,
        #   the new user and identity are the only entries.
        from .models import User, Identity
        user = DBSession.query(User).first()
        identity = user.identities[0]
        identifier = 'http://michaelmulich.myopenid.com/'
        self.assertEqual(identity.identifier, identifier)
        self.assertEqual(302, resp.status_int)
        parsed_location = urlparse(resp.location)
        self.assertEqual(parsed_location.scheme, 'https')
        self.assertEqual(parsed_location.netloc, domain)
        self.assertEqual(parsed_location.path, '/valid')
        query = parse_qs(parsed_location.query)
        # Note, it is not important to check the contents of the token here,
        #   because this is something that should/does happen in another test.
        self.assertIn('token', query)
        self.assertEqual(query['next'][0], came_from)

    def test_remote_login_w_existing_identity(self):
        # Case where the identity exists, therefor the user exists. This
        #   case will reauthenticate a user and send the back to the remote
        #   service.
        identifier = "http://philschatz.myopenid.com/"
        identity_id, user_id = self._make_identity(
            identifier, TEST_OPENID_IDENTS[1])
        request = self._make_one(TEST_OPENID_IDENTS[1])
        domain = 'example.com'
        port = 8080
        came_from = "http://{}:{}/foo/bar".format(domain, port)
        from .views import REFERRER_SESSION_KEY
        request.session[REFERRER_SESSION_KEY] = {
            'domain': domain,
            'port': port,
            'came_from': came_from,
            }

        from .views import login_complete
        with transaction.manager:
            resp = login_complete(request)

        # Since this is the first visitor and the database is empty,
        #   the new user and identity are the only entries.
        from .models import User, Identity
        user = DBSession.query(User).first()
        identity = user.identities[0]
        self.assertEqual(identity.identifier, identifier)
        self.assertEqual(302, resp.status_int)
        parsed_location = urlparse(resp.location)
        self.assertEqual(parsed_location.scheme, 'https')
        self.assertEqual(parsed_location.netloc, domain)
        self.assertEqual(parsed_location.path, '/valid')
        query = parse_qs(parsed_location.query)
        # Note, it is not important to check the contents of the token here,
        #   because this is something that should/does happen in another test.
        self.assertIn('token', query)

    def test_remote_local_login_w_new_identity(self):
        # Case where the identity/user exists and is being called by
        #   a remote service that is running locally alongside the cnx-user
        #   service.
        # Case for a completely new visitor logging into a remote service
        #   that is using cnx-user.
        self.config.registry.settings['allow-local-services'] = True
        request = self._make_one()
        domain = 'localhost'
        port = 8080
        scheme = 'http'
        came_from = "http://{}:{}/foo/bar".format(domain, port)
        from .views import REFERRER_SESSION_KEY
        request.session[REFERRER_SESSION_KEY] = {
            'domain': domain,
            'port': port,
            'came_from': came_from,
            }

        from .views import login_complete
        with transaction.manager:
            resp = login_complete(request)

        # Since this is the first visitor and the database is empty,
        #   the new user and identity are the only entries.
        from .models import User, Identity
        user = DBSession.query(User).first()
        identity = user.identities[0]
        identifier = 'http://michaelmulich.myopenid.com/'
        self.assertEqual(identity.identifier, identifier)
        self.assertEqual(302, resp.status_int)
        parsed_location = urlparse(resp.location)
        self.assertEqual(parsed_location.scheme, scheme)
        self.assertEqual(parsed_location.netloc, '{}:{}'.format(domain, port))
        self.assertEqual(parsed_location.path, '/valid')
        query = parse_qs(parsed_location.query)
        # Note, it is not important to check the contents of the token here,
        #   because this is something that should/does happen in another test.
        self.assertIn('token', query)
        self.assertEqual(query['next'][0], came_from)


class CheckTests(unittest.TestCase):
    # These tests assume a remote (or local) service is communicating with
    #   this service to verify the token it was given is valid.

    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        # Initialize the routes required by the view to generate
        #   followup urls.
        from . import register_api
        register_api(self.config)
        # The token store needs access to our sql-url at runtime.
        self._tmp_db_file = tempfile.mkstemp('test.db')[1]
        sql_connect_str = 'sqlite:///{}'.format(self._tmp_db_file)
        self.config.registry.settings['sqlalchemy.url'] = sql_connect_str

    def tearDown(self):
        os.remove(self._tmp_db_file)
        DBSession.remove()
        testing.tearDown()

    def test_request(self):
        # Check that a remote service (the indented usage) can make
        #   a request to this service and retrieve the correct user id.
        request = testing.DummyRequest()
        request.server_name = 'localhost'

        token = str(uuid.uuid4())
        request.params = request.POST = request.GET = {'token': token}

        from .views import get_token_store
        token_store = get_token_store()
        user_id = '1234-5678-90'
        token_store.store(token, user_id)

        from .views import check
        data = check(request)

        self.assertEqual(data['id'], user_id)
        url = request.route_url('get-user', user_id=user_id)
        self.assertEqual(data['url'], url)

    def test_fails_on_expired(self):
        self.fail("Has not been implemented yet.")
