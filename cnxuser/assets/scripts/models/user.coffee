define [
  'underscore'
  'backbone'
], (_, Backbone) ->

  return Backbone.Model.extend
    urlRoot: '/api/users'
    defaults:
      firstname: ''
      middlename: ''
      lastname: ''
      email: ''

    initialize: () ->
      @fetch()
