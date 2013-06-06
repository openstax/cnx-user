define [
  'underscore'
  'backbone'
  'cs!models/user'
], (_, Backbone, User) ->

  return new (Backbone.Collection.extend
    url: User.urlRoot
    model: User
  )()
