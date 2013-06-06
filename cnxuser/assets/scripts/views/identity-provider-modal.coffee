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

    events:
      'click #submit': 'submit'
      'click #cancel': 'cancel'

    render: ->
      @template = template(@model.toJSON())
      @$el.empty().append(@template)
      @$el.find('.modal').modal('show')
      if @model?.autosubmit
        @submit()

      return @

    cancel: ->
      @$el.find('.modal').modal('hide')
      @close()

    submit: ->
      # Remember to hide the modal on submission failure.
      @$('form').submit()
