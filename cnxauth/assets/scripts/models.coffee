define [
  'underscore'
  'backbone'
], (_, Backbone) ->

  _IdentityProvider = Backbone.Model.extend()

  IdentityProviders = Backbone.Collection.extend
    url: '/api/identity-providers'
    model: _IdentityProvider
    initialize: ->
      @fetch reset: true
  return {
    IdentityProviders: IdentityProviders
    }
