# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import unittest
import transaction

from pyramid import testing

from .models import DBSession


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
            jone_ident = Identity(jone_identifier, user=user)
            hao_ident = Identity(hao_identifier, user=user)
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
