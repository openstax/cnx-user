define [
  'jquery'
  'underscore'
  'backbone'
  'cs!models/user'
  'cs!views/base'
  'hbs!templates/profile'
], ($, _, Backbone, BaseView, template) ->

    return BaseView.extend
      initialize: (id) ->
        if !id then throw 'The profile view must be instantiated with a user ID.'

        @model = new User({id: id})
        @listenTo(@model, 'change', @render)

        @template = template(@model.toJSON())

      render: () ->
        @$el.html(@template)

        return @
