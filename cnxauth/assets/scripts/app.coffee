define [
  'jquery'
  'underscore'
  'backbone'
  'cs!models'
  'cs!views'
  'less!styles/main.less'
], ($, _, Backbone, models, views) ->

  router = new Backbone.Router
  router.route '', 'index', ->
    view = new views.SplashView
      el: '[role=main]'
    view.render()
  router.route 'register', 'register', ->
    # Pass in the authentication identity provider collection.
    providers = new models.IdentityProviders()
    providers.fetch reset: true
    view = new views.RegistrationView
      el: '[role=main]'
      collection: providers
    view.render()
  router.route 'login', 'login', ->
    # Pass in the authentication identity provider collection.
    ##providers = models.IdentityProviders
    view = new views.LoginView
      el: '[role=main]'
      ##collection: providers
    view.render()
  router.route 'users/:id', 'profile', (id) ->
    ##profile = models.Profile
    view = new views.ProfileView
      el: '[role=main]'
      ##model: profile
    view.render()

  # Intercept all clicks on 'a' tags.
  $(document).on 'click', 'a:not([data-bypass])', (e) ->
    external = new RegExp('^((f|ht)tps?:)?//')
    href = $(@).attr('href')

    e.preventDefault()

    if external.test(href)
      window.open(href, '_blank')
    else
      router.navigate(href, {trigger: true})

  # Start the HTML5 history/pushState interface, which allows for
  #   URL navigation.
  Backbone.history.start pushState: true

  return router
