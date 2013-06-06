define [
  'jquery'
  'underscore'
  'backbone'
  'cs!views/base'
  'hbs!templates/login'
], ($, _, Backbone, BaseView, template) ->

    return BaseView.extend
      render: ->
        @$el.html template
        return @

      close: () ->
        @remove();
        @unbind();
