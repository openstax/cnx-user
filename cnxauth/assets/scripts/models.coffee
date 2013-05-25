define [
  'underscore'
  'backbone'
], (_, Backbone) ->

  _IdentityProvider = Backbone.Model.extend()

  IdentityProviders = Backbone.Collection.extend
    url: '/api/identity-providers'
    model: _IdentityProvider
  return {
    IdentityProviders: IdentityProviders
    }
