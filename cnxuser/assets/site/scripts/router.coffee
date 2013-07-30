define [
  'jquery'
  'underscore'
  'backbone',
  'cs!views/app'
], ($, _, Backbone, appView) ->

  return new (Backbone.Router.extend
    routes:
      '': 'index',
      'register': 'register',
      # XXX Assigned to register because it's the same functionality,
      #     but the wording is different. And since the wording hasn't
      #     been thought about yet, all we need is the functionality.
      'login': 'register',
      'users/:id': 'profile',

      # Default Route
      '*actions': 'index'

    index: () ->
      appView.render('splash')

    register: () ->
      appView.render('register')

    login: () ->
      appView.render('login')

    profile: (param) ->
      appView.render('profile', {id: param})
  )()
