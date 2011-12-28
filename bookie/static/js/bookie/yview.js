/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */
YUI.add('bookie-view', function (Y) {
    var _ = Y.Lang.substitute;

    Y.namespace('bookie');

    Y.bookie.BmarkView = Y.Base.create('bookie-bmark-view', Y.View, [], {
        container_html: '<div class="bmark"/>',
        template: Y.one('#bmark_row').get('text'),

        events: {
            '.delete': {
                click: 'remove'
            }
        },

        initializer: function (cfg) {
            this.cTemplate = Y.Handlebars.compile(this.template);

            // hold onto the idea that we only take Bmark objects for the
            // moment...
            // console.log(cfg.model instanceof Y.bookie.Bmark);
        },

        /**
         * Handle the remove event on this bookmark
         *
         */
        remove: function () {
            var that = this;
            this.get('model').remove();

            this.get('container').transition({
                easing: 'ease-out',
                duration: .4,
                display: 'none'
            }, function() {
                that.destroy();
            });
        },

        render: function () {
            // Render this view's HTML into the container element.
            var tpl_data = Y.mix(
                {username: this.get('resource_user')},
                this.get('model').getAttrs()
            );

            return this.get('container').set(
                'innerHTML',
                this.cTemplate(tpl_data)
            );
        }
    }, {
        ATTRS: {
            /**
             * The view is for a url of a specific user
             *
             * Say /admin/bmarks for the admin bookmarks, does not mean I'm
             * the admin
             *
             */
            resource_user: {
            },

            /**
             * The currently authorized user
             *
             */
            current_user: {
            },

            container: {
                valueFn: function() {
                    var container = Y.Node.create(this.container_html);
                    container.set(
                        'data-bid',
                         this.get('model').get('bid')
                    );
                    return container;
                }

            }
        }
    });

}, '0.1.0', { requires: ['base', 'view', 'bookie-model', 'node-event-simulate', 'handlebars', 'transition'] });
