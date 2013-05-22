define [
  'jquery'
  'underscore'
  'backbone'
  'hbs!templates/splash'
  'hbs!templates/register'
  'hbs!templates/login'
  'hbs!templates/profile'
], ($, _, Backbone, splashTmpl, registrationTmpl, loginTmpl,
    profileTmpl) ->
  return {
    SplashView: Backbone.View.extend
      render: ->
        @$el.html splashTmpl
        return @
    RegistrationView: Backbone.View.extend
      initialize: ->
        @listenTo(@collection, 'reset', @render)
      render: ->
        template = registrationTmpl providers: @collection.toJSON()
        @$el.html template
        return @
    LoginView: Backbone.View.extend
      render: ->
        @$el.html loginTmpl
        return @
    ProfileView: Backbone.View.extend
      render: ->
        template = profileTmpl model: @model
        @$el.html template
        return @
    }
