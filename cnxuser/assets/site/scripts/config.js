(function () {
    'use strict';

    require.config({
        // # Paths
        paths: {
            // ## Template and Style paths
            templates: '../templates',
            styles: '../styles',

            // ## Requirejs plugins
            text: 'libs/requirejs-text/text',
            hbs: 'libs/require-handlebars-plugin/hbs',
            cs: 'libs/require-cs/cs',

            // ## Core Libraries
            jquery: 'libs/jquery/jquery',
            underscore: 'libs/lodash/lodash',
            backbone: 'libs/backbone/backbone',

            // ## UI Libraries
            // Boostrap Plugins
            bootstrapAffix: 'libs/bootstrap/js/bootstrap-affix',
            bootstrapAlert: 'libs/bootstrap/js/bootstrap-alert',
            bootstrapButton: 'libs/bootstrap/js/bootstrap-button',
            bootstrapCarousel: 'libs/bootstrap/js/bootstrap-carousel',
            bootstrapCollapse: 'libs/bootstrap/js/bootstrap-collapse',
            bootstrapDropdown: 'libs/bootstrap/js/bootstrap-dropdown',
            bootstrapModal: 'libs/bootstrap/js/bootstrap-modal',
            bootstrapPopover: 'libs/bootstrap/js/bootstrap-popover',
            bootstrapScrollspy: 'libs/bootstrap/js/bootstrap-scrollspy',
            bootstrapTab: 'libs/bootstrap/js/bootstrap-tab',
            bootstrapTooltip: 'libs/bootstrap/js/bootstrap-tooltip',
            bootstrapTransition: 'libs/bootstrap/js/bootstrap-transition',

            // ## Handlebars Dependencies
            Handlebars: 'libs/require-handlebars-plugin/Handlebars',
            i18nprecompile: 'libs/require-handlebars-plugin/hbs/i18nprecompile',
            json2: 'libs/require-handlebars-plugin/hbs/json2',

            // ## CoffeeScript Compiler
            'coffee-script': 'libs/coffee-script/index'
        },

        // # Packages
        packages: [{
            name: 'css',
            location: 'libs/require-css',
            main: 'css'
        }, {
            name: 'less',
            location: 'libs/require-less',
            main: 'less'
        }],

        // # Shims
        shim: {
            // ## Core Libraries
            underscore: {
                exports: '_'
            },
            backbone: {
                deps: ['underscore', 'jquery'],
                exports: 'Backbone'
            },

            // ## UI Libraries
            // # Bootstrap Plugins
            bootstrapAffix: ['jquery'],
            bootstrapAlert: ['jquery'],
            bootstrapButton: ['jquery'],
            bootstrapCarousel: ['jquery'],
            bootstrapCollapse: ['jquery'],
            bootstrapDropdown: ['jquery'],
            bootstrapModal: ['jquery', 'bootstrapTransition'],
            bootstrapPopover: ['jquery', 'bootstrapTooltip'],
            bootstrapScrollspy: ['jquery'],
            bootstrapTab: ['jquery'],
            bootstrapTooltip: ['jquery'],
            bootstrapTransition: ['jquery'],
            bootstrapTypeahead: ['jquery']
        },

        // Handlebars Requirejs Plugin Configuration
        // Used when loading templates `'hbs!...'`.
        hbs: {
            disableI18n: true,
            helperPathCallback: function (name) {
                return 'cs!templates/handlebars/' + name;
            },
            templateExtension: 'html'
        }
    });

})();
