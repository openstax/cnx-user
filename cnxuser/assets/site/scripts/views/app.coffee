define [
  'jquery'
  'underscore'
  'backbone'
  'less!styles/main'
], ($, _, Backbone) ->

  _lastView = null

  return new (Backbone.View.extend
    el: 'body'

    render: (page, options) ->
      # Lazy-load the page
      require ["cs!views/#{ page }"], (View) ->
        _lastView?.close()
        
        view = new View(options)
        view.setElement($('#main')).render()

      return @
  )()
