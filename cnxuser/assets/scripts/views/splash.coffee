define [
  'jquery'
  'underscore'
  'backbone'
  'cs!views/base'
  'hbs!templates/splash'
], ($, _, Backbone, BaseView, template) ->

    return BaseView.extend
      render: ->
        @$el.html(template)
        return @
