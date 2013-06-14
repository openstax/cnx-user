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
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
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
    config.add_route('get-users', '/users')
    config.add_route('get-user', '/users/{user_id}')
    config.add_route('put-user', '/users/{user_id}')
    config.add_route('get-user-identities', '/users/{user_id}/identities')
    config.add_route('get-user-identity',
                     '/users/{user_id}/identities/{identity_id}')
    config.add_route('delete-user-identity',
                     '/users/{user_id}/identities/{identity_id}')


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
    # XXX After the initial implementation this needs to be revisited
    #     for clarity. The velruse registration should closely reflect
    #     pyramid style plugin registration.
    settings = config.registry.settings

    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['session.secret'],
        )
    config.set_session_factory(session_factory)

    from ._velruse import openid, google, IActiveIdentityProviders
    # XXX identity providers are currently hard coded. This needs to
    #     be a settings value.
    providers = [openid, google]
    config.registry.registerUtility(providers, IActiveIdentityProviders)
    for provider in providers:
        config.registry.registerUtility(provider, name=provider.id)

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


def set_up_service_exchange(config):
    """Initializes and configures the parts of the application that handle
    token creation and validation for external services using this user
    profile and authentication hub.
    """
    # Part of the single sign-on design. This provides background
    #   communication for the connecting service.
    config.add_route('server-check', '/server/check')


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    authentication_policy = AuthTktAuthenticationPolicy(
            secret=settings['auth.secret'],
            ##callback=group_finder,
            hashalg=settings.get('auth.hash-algorithm', 'sha512'),
            )
    config.set_authentication_policy(authentication_policy)
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authorization_policy)

    # Route registration
    config.include(register_bbb)
    config.include(register_api, route_prefix='/api')
    config.include(set_up_velruse)
    config.include(set_up_service_exchange)
    config.include(register_www_iface)
    config.scan()
    return config.make_wsgi_app()
