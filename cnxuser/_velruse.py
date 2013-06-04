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

import velruse
from zope.interface import implementer, Attribute, Interface
from pyramid.threadlocal import get_current_request


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


class IIdentityProvider(Interface):
    """Contains information about an identity and special methods to get
    other information about the identity."""

    id = Attribute("identifier that matches with the ``velruse``.")
    name = Attribute("Human readible name for the identity provider.")
    location = Attribute("URL where the login sequence should begin and the"
                         "field values should be submitted.")

    fields = Attribute("A list of fields required by the identity provider.")
    auto_submit = Attribute("Boolean value for determining if a form can be"
                            "auto submitted. Usually not if user input"
                            "is required.")


class IActiveIdentityProviders(Interface):
    """Utility that contains a sequence of active registered
    identity providers."""


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
