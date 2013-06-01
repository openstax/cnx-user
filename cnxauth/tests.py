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
import tempfile
from urlparse import parse_qs, urlparse

import transaction
from pyramid import testing

from .models import DBSession


here = os.path.abspath(os.path.dirname(__file__))
test_data_directory = os.path.join(here, 'test-data')
with open(os.path.join(test_data_directory, 'idents.json'), 'r') as fp:
    _TEST_IDENTS = json.load(fp)
TEST_OPENID_IDENTS = _TEST_IDENTS['openid']
TEST_GOOGLE_IDENTS = _TEST_IDENTS['google']


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
        sql_connect_str = 'sqlite:///{}'.format(_db_file)
        request.registry.settings['sqlalchemy.url'] = sql_connect_str
        # Attach a token to the request, which would have happened at
        #   login through the event hooks I put in velruse.
        domain = 'example.com'
        referrer = "http://{}:8080/foo/bar".format(domain)
        request.referrer = referrer
        from velruse.events import AfterLogin
        from .views import capture_referrer
        capture_referrer(AfterLogin(request))

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
        self.assertEqual(int(token_user_id), user.id)
