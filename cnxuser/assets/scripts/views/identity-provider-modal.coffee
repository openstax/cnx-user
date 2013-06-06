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
      if not @model then throw 'The identity provider modal must be instantiated with a model.'

      if not @el
        $('<div id="registration-modal">').appendTo($('body'))
        @setElement($('#registration-modal'))

      @template = template(@model.toJSON())

    render: ->
      @$el.html(@template)

      if @model.get('auto_submit')
        @autoSubmit()
      else
        @show()

      return @

    show: () ->
      @$el.find('.modal').modal('show')

    autoSubmit: () ->
      @$el.find('form').submit()
