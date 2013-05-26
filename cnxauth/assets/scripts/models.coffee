define [
  'underscore'
  'backbone'
], (_, Backbone) ->

  _IdentityProvider = Backbone.Model.extend()

  IdentityProviders = Backbone.Collection.extend
    url: '/api/identity-providers'
    model: _IdentityProvider

  User = Backbone.Model.extend
    urlRoot: '/api/users'
    defaults:
      firstname: ''
      middlename: ''
      lastname: ''
      email: ''

  Users = Backbone.Collection.extend
    url: User.urlRoot
    model: User

  return {
    IdentityProviders: IdentityProviders
    User: User
    Users: Users
    }
