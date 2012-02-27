/**
 * History Module, helping us wrap/deal with history changes.
 *
 * @namespace bookie
 * @module history
 *
 */
YUI.add('bookie-history', function (Y) {
    var ns = Y.namespace('bookie');

    ns.BmarkListHistory = Y.Base.create('bookie-history', Y.Base, [], {
        /**
         * Watch for any changes that should effect the history.
         *
         * @method _bind_events
         * @private
         *
         */
        _bind_events: function () {
            // not sure how I can watch for any attr change on the pager as a
            // whole
            this.get('pager').after('countChange', this._update, this);
            this.get('pager').after('pageChange', this._update, this);
            this.get('pager').after('with_contentChange', this._update, this);
            this.after('termsChange', this._update, this);

            // also watch for new tags being added
            // this will trigger a terms update and should rebuild our
            // url/state
            Y.on('tag:changed', function (e) {
                this.set('terms', e.tags);
            }, this);
        },

        /**
         * Construct a new url based on our data and route specified for the
         * current state of things.
         *
         * @method _build_url
         * @private
         *
         */
        _build_url: function () {
            debugger;
            var terms = this.get('terms').join('/');
            var pager = this.get('pager');
            var qs = Y.QueryString.stringify({
                count: pager.get('count'),
                page: pager.get('page'),
                with_content: pager.get('with_content')
            });

            return this.get('route') + '/' + terms + '?' + qs;
        },

        /**
         * Update the history based on the current state of the pager, terms
         *
         * @method _update
         * @param {Event} ev
         *
         */
        _update: function (ev) {

            debugger;
            this.history.add({
                pager: this.get('pager').getAttrs(),
                terms: this.get('terms')
            }, {
                title: 'Viewing page: ' + this.get('pager').get('page') + 1,
                url  : this._build_url()
            });
        },

        /**
         * General initializer
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            this.history = new Y.History({
                pager: this.get('pager').getAttrs(),
                terms: this.get('terms')
            });

            this._bind_events();
        }
    }, {
        ATTRS: {
            /**
             * @attribute the pager object weneed to construct our current
             * state from
             *
             * @default undefined
             * @type PagerModel
             * @required
             *
             */
            pager: {
                required: true
            },

            /**
             * The search terms/tags that have been used to generate the
             * current view.
             *
             * @attribute terms
             * @default []
             * @type Array
             *
             */
            terms: {
                value: [],
            },

            /**
             * What is the http route we're building a history for? For
             * instance, if we've loaded the /recent url, we'll need to append
             * our history params to the /recent url to build:
             *
             * /recent/term1?count=50&page=2&with_content=true
             *
             * @attribute route
             * @default undefined
             * @type string
             * @required
             *
             */
            route: {
                required: true
            }
        }
    });

}, '0.1', {
    requires: ['history', 'querystring']
});
