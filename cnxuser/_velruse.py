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
from zope.interface import implementer, Interface


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

OPENID = {
    'id': 'openid', 'name': 'OpenID',
    'fields': [{'type': 'text', 'name': 'openid_identifier',
                'label': "OpenID identifier string",
                'placeholder': 'http://me.example.com',
                },
               ],
    'auto_submit': False,
    }

GOOGLE = {
    'id': 'google', 'name': 'Google',
    'auto_submit': True,
    }

_registered_identity_providers = {
    'openid': OPENID,
    'google': GOOGLE,
    }


class IIdentityProviderRegistry(Interface):
    """Utility for poking at the registered identity providers'
    information."""


@implementer(IIdentityProviderRegistry)
class IdentityProviderRegistry(Mapping):

    def __getitem__(self, key):
        global _registered_identity_providers
        return _registered_identity_providers[key]

    def __iter__(self):
        global _registered_identity_providers
        return iter(_registered_identity_providers)

    def __len__(self):
        global _registered_identity_providers
        return len(_registered_identity_providers)
