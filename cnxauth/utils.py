# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###


__all__ = ('discover_uid',)

def discover_uid(auth_complete):
    """Finds the prefered user name or id in
    the given velruse.AuthenticationComplete object as 'auth_complete'."""
    # Has a preferred username been supplied?
    try:
        return auth_complete.profile['preferredUsername']
    except KeyError:
        # Couldn't be that easy. :(
        pass

    # Attempt to retrieve the uid from the accounts listing.
    accounts = auth_complete.profile['accounts']
    try:
        uid = accounts[0]['username']
    except IndexError:
        raise ValueError("Missing account values")
    return uid
