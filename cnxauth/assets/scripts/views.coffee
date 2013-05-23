define [
  'jquery'
  'underscore'
  'backbone'
  'hbs!templates/splash'
  'hbs!templates/register'
  'hbs!templates/login'
  'hbs!templates/profile'
  'hbs!templates/identity-provider-modal'
  'bootstrapModal'
], ($, _, Backbone, splashTmpl, registrationTmpl, loginTmpl,
    profileTmpl, identityProviderModalTmpl) ->

  IdentityProviderModal = Backbone.View.extend
    events:
      'click #submit': 'submit'
      'click #cancel': 'cancel'
    render: ->
      template = identityProviderModalTmpl @model.toJSON()
      @$el.empty().append template
      @$('.modal').modal('show')
      if @model.autosubmit? and @model.autosubmit is true
        @submit()
      return @
    cancel: ->
      @$('.modal').modal('hide')
      @remove()
    submit: ->
      # Remember to hide the modal on submission failure.
      @$('form').submit()

  return {
    SplashView: Backbone.View.extend
      render: ->
        @$el.html splashTmpl
        return @
    RegistrationView: Backbone.View.extend
      events:
        'click .register-control': 'takeAction'
      initialize: ->
        @listenTo(@collection, 'reset', @render)
      render: ->
        template = registrationTmpl providers: @collection.toJSON()
        @$el.html template
        return @
      takeAction: (event) ->
        provider_id = $(event.target).attr 'value'
        provider = @collection.findWhere id: provider_id
        control_space_id = 'registration-modal'
        $control_space = $(control_space_id)
        if $control_space.length == 0
          control_space = $("<div id=\"#{control_space_id}\">").appendTo(@el)[0]
        else
          control_space = $control_space[0]
        secondary = new IdentityProviderModal
          el: control_space
          model: provider
        secondary.render()  # This may submit a form.
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
