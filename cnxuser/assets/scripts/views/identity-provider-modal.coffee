define [
  'jquery'
  'underscore'
  'backbone'
  'cs!views/base'
  'hbs!templates/identity-provider-modal'
  'bootstrapModal'
], ($, _, Backbone, BaseView, template) ->

  return BaseView.extend
    el: '#registration-modal'

    initialize: () ->
      if not @el
        $('<div id="registration-modal">').appendTo($('body'))
        @setElement($('#registration-modal'))

    render: ->
      @template = @template or template(@model.toJSON())
      @$el.empty().append(@template)
      @$el.find('.modal').modal('show')

      return @
