define [
  'underscore'
  'backbone'
], (_, Backbone) ->

  return new (Backbone.Collection.extend
    url: '/api/identity-providers'
    
    initialize: () ->
      @fetch()
  )()
