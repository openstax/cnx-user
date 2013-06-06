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
      initialize: () ->
        @listenTo(identityProviders, 'reset', @render)

      render: () ->
        @template = template({providers: identityProviders.toJSON()})
        @$el.html(@template)

        return @
      
      events:
        'click .register-control': 'register'

      register: (e) ->
        provider = identityProviders.get($(e.currentTarget).data('id'))

        modal = new IdentityProviderModal({model: provider})
        modal.render()
