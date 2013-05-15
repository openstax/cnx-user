# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Authentication and user profile web application"""
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def register_api(config):
    config.add_route('identifier', '/ident/{id}')
    config.add_route('post-user', '/users/')
    config.add_route('get-user', '/users/{id}')
    config.add_route('put-user', '/users/{id}')
    config.add_route('query', '/users/query')

def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    ##config.add_static_view('static', 'static', cache_max_age=3600)
    config.include(register_api, route_prefix='/api')
    config.scan()
    return config.make_wsgi_app()
