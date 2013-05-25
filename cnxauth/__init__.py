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
from pyramid.session import UnencryptedCookieSessionFactoryConfig

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
    config.add_route('catch-all', '/*path')
    # These routes are deliberately placed after the catch-all route,
    #   because they are not wired to any on-server views. They are
    #   however wired into the client-side/front-end routes framework.
    config.add_route('www-get-user', '/users/{id}')


def set_up_velruse(config):
    """Initialize and configure Velruse as a plugin. See also:
    http://pythonhosted.org/velruse/usage.html#as-a-pyramid-plugin
    """
    # XXX identity providers are currently hard coded. This needs to
    #     be a settings value.
    # XXX After the initial implementation this needs to be revisited
    #     for clarity.
    settings = config.registry.settings

    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['session.secret'],
        )
    config.set_session_factory(session_factory)

    # Most of these providers have loaders for settings. OpenID is one
    #   of them that doesn't. =/  Refactor later please. :)
    config.include('velruse.providers.openid')
    config.add_openid_login(realm=settings.get('velruse.openid.realm'),
                            storage=None,  # Defaults to in-memory storage.
                            login_path='/server/login/openid',
                            callback_path='/server/login/openid/callback',
                            )

    config.include('velruse.providers.google_oauth2')
    config.add_google_oauth2_login_from_settings()


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include(register_bbb)
    config.include(register_api, route_prefix='/api')
    config.include(set_up_velruse)
    config.include(register_www_iface)
    config.scan()
    return config.make_wsgi_app()
