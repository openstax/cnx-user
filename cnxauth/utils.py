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
    accounts = auth_complete.profile['accounts']
    try:
        uid = accounts[0]
    except IndexError:
        raise ValueError("Missing account values")
