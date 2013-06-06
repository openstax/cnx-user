define [
  'jquery'
  'underscore'
  'backbone'
  'cs!views/base'
  'hbs!templates/identity-provider-modal'
  'bootstrapModal'
], ($, _, Backbone, BaseView, template) ->

  return BaseView.extend
    events:
      'click #submit': 'submit'
      'click #cancel': 'cancel'

    render: ->
      @template = template(@model.toJSON())
      @$el.empty().append(@template)
      @$el.modal('show')
      if @model?.autosubmit
        @submit()

      return @

    cancel: ->
      @$el.modal('hide')
      @close()

    submit: ->
      # Remember to hide the modal on submission failure.
      @$('form').submit()
