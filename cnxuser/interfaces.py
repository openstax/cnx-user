# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
from zope.interface import Attribute, Interface

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


class IUser(Interface):
    """Implemented by the user model"""


class IIdentity(Interface):
    """Implemented by the identity model"""


class ILoginDataExtractor(Interface):
    """An adapter for IUser and IIdentity objects to assign identity profile
    data to user"""
    id = Attribute('Identifier of identity provider')

    def __init__(user, identity):
        """IUser and IIdentity"""

    def __call__():
        """Assign identity profile data to user"""
