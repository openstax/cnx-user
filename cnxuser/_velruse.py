# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""\
A supplemental module for the ``velruse`` package. This module adds predefined
data sets for identity providers that allows the application to build
necessary functions, forms and views around the identiy provider.
"""
from collections import Mapping
import json

import velruse
from zope.interface import implements, implementer
from pyramid.threadlocal import get_current_request

from .interfaces import IIdentityProvider, ILoginDataExtractor


@implementer(IIdentityProvider)
class IdentityProvider:
    """See IIdentityProvider"""

    def __init__(self, id, name, fields=[], auto_submit=False):
        self.id = id
        self.name = name
        self.fields = fields
        self.auto_submit = auto_submit

    @property
    def location(self):
        request = get_current_request()
        return velruse.login_url(request, self.id)

    def __json__(self, request):
        return {'id': self.id, 'name': self.name,
                'location': self.location,
                'fields': self.fields, 'auto_submit': self.auto_submit,
                }


OPENID = {
    'id': 'openid', 'name': 'OpenID',
    'fields': [{'type': 'text', 'name': 'openid_identifier',
                'label': "OpenID identifier string",
                'placeholder': 'http://me.example.com',
                },
               ],
    'auto_submit': False,
    }
openid = IdentityProvider(**OPENID)

GOOGLE = {
    'id': 'google', 'name': 'Google',
    'auto_submit': True,
    }
google = IdentityProvider(**GOOGLE)


class GoogleLoginDataExtractor(object):
    implements(ILoginDataExtractor)

    id = 'google'

    def __init__(self, user, identity):
        self.user = user
        self.identity = identity
        self.profile = json.loads(self.identity.profile)

    def __call__(self):
        self.user.email = self.profile.get('verifiedEmail')
        self.user.fullname = self.profile.get('displayName')
