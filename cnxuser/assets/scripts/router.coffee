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
      'login': 'login',
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
