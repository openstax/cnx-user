define [
  'jquery'
  'underscore'
  'backbone'
  'cs!views/base'
  'cs!collections/identity-providers'
  'cs!views/identity-provider-modal'
  'hbs!templates/register'
], ($, _, Backbone, BaseView, identityProviders, IdentityProviderModal, template) ->

    return BaseView.extend
      events:
        'click .register-control': 'takeAction'

      initialize: () ->
        @listenTo(identityProviders, 'reset', @render)

      render: () ->
        @template = template({providers: identityProviders.toJSON()})
        @$el.html(@template)

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
        secondary = new IdentityProviderModal()
          el: control_space
          model: provider
        secondary.render()  # This may submit a form.
        return @
