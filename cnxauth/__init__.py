# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Authentication and user profile web application"""
from pyramid.config import Configurator
from pyramid.static import static_view
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

def register_bbb(config):
    """Registers the backwards compatible application programming
    interface (API)."""
    # TODO bring these back
    pass

def register_api(config):
    """Registers the application programing interface (API)."""
    config.add_route('identity-providers', '/identity-providers')
    config.add_route('post-user', '/users/')
    config.add_route('get-user', '/users/{id}')
    config.add_route('put-user', '/users/{id}')
    config.add_route('query', '/users/query')

def register_www_iface(config):
    """Registers routes and assets for the web interface."""
    config.add_static_view('scripts', 'assets/scripts', cache_max_age=0)
    config.add_static_view('styles', 'assets/styles', cache_max_age=0)
    config.add_static_view('templates', 'assets/templates', cache_max_age=0)
    config.add_route('index', '/')
    config.add_route('catchall', '/*path')

def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include(register_bbb)
    config.include(register_api, route_prefix='/api')
    config.include(register_www_iface)
    config.scan()
    return config.make_wsgi_app()
