# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.exceptions import NotFound
from pyramid.view import view_config

from . import usermodel


logger = logging.getLogger('cnxauth')


@view_config(name='identifier', request_method='GET', renderer='json')
def get_user_by_identifier(request):
    ident = request.matchdict['id']
    try:
        user = usermodel.get_user_by_identifier(ident)
    except err.Rhaptos2Error, e:
        raise NotFound()
    return {'id': user.id, 'identifier': user.identifier, 'type': user.type}


@view_config(name='get-user', request_method='GET', renderer='json')
def get_user(request):
    id = request.multidict['id']
    try:
        user = usermodel.get_user(id)
    except err.Rhaptos2Error, e:
        raise NotFound()
    return {'id': user.id, 'fullname': user.fullname, 'email': user.email}


@view_config(name='post-user', request_method=['POST', 'PUT'])
def post_user(request):
    id = request.multidict.get('id', None)
    data = request.json_body
    if request.method == 'PUT' and id is None:
        raise HttpBadRequest("PUT without an ID")
    elif request.metho == 'POST':
        user = usermodel.post_user(data)
    else:
        user = usermodel.put_user(data, id)
    return "Saved"


@view_config(name='query', request_method='GET', renderer='json')
def query(request):
    q = request.query_string.get('q', '')
    try:
        matchlist = usermodel.get_user_by_name(q)
    except err.Rhaptos2Error, e:
        raise HTTPInternalServerError()
    return [u.id for u in matchlist]
