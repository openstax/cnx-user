define [
  'jquery'
  'underscore'
  'backbone'
], ($, _, Backbone) ->

  return Backbone.View.extend
    close: () ->
      @stopListening()
      @remove()
      @unbind()
