/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */
YUI.add('bookie-view', function (Y) {
    var _ = Y.Lang.substitute;

    Y.namespace('bookie');

    Y.bookie.BmarkView = Y.Base.create('bookie-bmark-view', Y.View, [], {
        template: "{{id}}",

        events: {
            '.remove': {
                click: 'remove'
            }
        },

        initializer: function (cfg) {
            this.cTemplate = Handlebars.compile(this.template)
            // hold onto the idea that we only take Bmark objects for the
            // moment...
            // console.log(cfg.model instanceof Y.bookie.Bmark);
        },

        render: function (parent) {
            // Render this view's HTML into the container element.
            parent.setContent(
                this.cTemplate(this.model.getAttrs())
            );
        }
    });

}, '0.1.0', { requires: ['base', 'view', 'bookie-model'] });
