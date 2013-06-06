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


class RegistrationAndLoginViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        # The following is used to register the routes used by the view.
        from . import register_www_iface
        register_www_iface(self.config)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_first_local_visit(self):
        # As a first time visitor, I'd like to register and then edit my
        #   profile, because I'd like to have this this service with
        #   other CNX services.
        # This case illustrates a first time visitor that is directly
        #    interacting (not forwarded via another service) with the
        #    service. This case not does deal with actually editing
        #    the profile, but getting the visitor to a place where
        #    they can edit the profile.
        request = testing.DummyRequest()
        # Create the request context.
        from velruse import AuthenticationComplete
        test_ident = TEST_OPENID_IDENTS[0]
        request.context = AuthenticationComplete(**test_ident)

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
        self.assertEqual(request.route_url('www-get-user', id=user.id),
                         resp.location)
        self.assertEqual(302, resp.status_int)

    def test_first_remote_visit(self):
        # As a first time visitor coming from a remote service, I want
        #   to login and be returned to the service I started from.
        # This case illustrates a first time visitor that is coming
        #   from a remote service. The goal here is to authenticate
        #   the visitor and provide them with a token in the redirect
        #   back to the remote service.

        # The 'anykeystore' package's sqlalchemy keystore does not
        #   support a persistent connection, so we must use a file
        #   based sqlite DB.
        _db_file = tempfile.mkstemp('test.db')[-1]
        self.addCleanup(os.remove, _db_file)

        request = testing.DummyRequest()
        request.server_name = 'localhost'
        sql_connect_str = 'sqlite:///{}'.format(_db_file)
        request.registry.settings['sqlalchemy.url'] = sql_connect_str
        # Attach a token to the request, which would have happened at
        #   login through the event hooks I put in velruse.
        domain = 'example.com'
        referrer = "http://{}:8080/foo/bar".format(domain)
        request.referrer = referrer
        from velruse.events import AfterLogin
        from .views import capture_requesting_service
        # Note, this causes the test to ping the network using
        #   the 'socket' library.
        capture_requesting_service(AfterLogin(request))

        # Create the request context.
        from velruse import AuthenticationComplete
        test_ident = TEST_OPENID_IDENTS[0]
        request.context = AuthenticationComplete(**test_ident)

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

        # Is the request a redirect to the service's 'valid' url?
        self.assertEqual(302, resp.status_int)
        expected_location = 'https://{}/valid'.format(domain)
        self.assertTrue(resp.location.find(expected_location) >= 0)

        # Verify the token has the correct information.
        parsed_location = urlparse(resp.location)
        parsed_token = parse_qs(parsed_location.query)['token'][0]
        # Note that we aren't testing 'anykeystore' here so it's ok to use.
        from .views import get_token_store
        token_storage = get_token_store()
        token_value = token_storage.retrieve(parsed_token)
        token_user_id, token_domain = token_value.split('%')
        self.assertEqual(token_domain, domain)
        self.assertEqual(uuid.UUID(token_user_id), user.id)

    def test_backchannel_token_check(self):
        # As a remote service, I want to check the validation token
        #   that I was given by the visitor from the authentication
        #   service is a valid request for service and I need it in
        #   order to associate the visitor with a user profile in the
        #   authenticate service.
        # This case walks through a request from a remote service to
        #   check if the given token is indeed valid. The goal here is
        #   to verify and retrieve the user id from the authentication
        #   service (this application).

        # The 'anykeystore' package's sqlalchemy keystore does not
        #   support a persistent connection, so we must use a file
        #   based sqlite DB.
        _db_file = tempfile.mkstemp('test.db')[-1]
        self.addCleanup(os.remove, _db_file)

        request = testing.DummyRequest()

        # Make the request look as if it's coming from an remote service.
        domain, ip_address = _resolve_test_domain('example.com')
        request.remote_addr = ip_address

        # Assign the sqla connection string for the key store lookup.
        sql_connect_str = 'sqlite:///{}'.format(_db_file)
        request.registry.settings['sqlalchemy.url'] = sql_connect_str

        # Create the token entry.
        from .views import get_token_store
        token_storage = get_token_store()
        token = str(uuid.uuid4())
        user_id = 7654
        token_storage.store(token, "{}%{}".format(user_id, domain))

        # Put the token in the request as a POST value.
        request.POST = MultiDict()
        request.POST['token'] = token
        request.params = request.POST

        from .views import check
        with transaction.manager:
            resp = check(request)

        self.assertEqual(resp, str(user_id))
