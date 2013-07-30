define [
  'jquery'
  'underscore'
  'backbone'
  'cs!views/base'
  'cs!models/user'
  'hbs!templates/profile'
], ($, _, Backbone, BaseView, User, template) ->

  return BaseView.extend
    initialize: (id) ->
      if !id then throw new Error('The profile view must be instantiated with a user ID.')

      @model = new User(id)
      @listenTo(@model, 'change', @render)

      @template = template(@model.toJSON())

    render: () ->
      @$el.html(@template)

      return @
