define [
  'underscore'
  'backbone'
], (_, Backbone) ->

  User = Backbone.Model.extend
    urlRoot: '/api/users'
    defaults:
      firstname: ''
      middlename: ''
      lastname: ''
      email: ''

    initialize: () ->
      @fetch({reset: true})
