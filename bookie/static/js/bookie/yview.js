/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */
/**
 * Bookie's View objects used to represent pages or parts of page content.
 *
 * @namespace bookie
 * @module view
 *
 */
YUI.add('bookie-view', function (Y) {
    var _ = Y.substitute,
        ns = Y.namespace('bookie');

    /**
     * Display a list of bookmarks from the API to the end user.
     *
     * @class BmarkListView
     * @extends Y.View
     *
     */
    ns.BmarkListView = Y.Base.create('bookie-list-view', Y.View, [], {
        container_html: '<div class="bmark_list"/>',
        _get_template: function () {
            return Y.one('#bmark_list').get('text');
        },

        events: {},

        /**
         * Prepare and add the pager view for our control
         *
         * We need two, one for the top and one for the bottom
         *
         * @method _init_pager
         * @private
         *
         */
        _init_pager: function () {
            this.pagers = [
                new Y.bookie.PagerView(),
                new Y.bookie.PagerView(),
            ];

            // bind the pager event
            Y.on('pager:next', this._next_page, this);
            Y.on('pager:previous', this._prev_page, this);
        },

        /**
         * Setup the api call for filling in our data based on our config
         *
         * @method _init_api
         * @private
         *
         */
        _init_api: function () {
            var api_callable = this.get('api_callable');
            this.api = new api_callable(this.get('api_cfg'));
        },

        /**
         *
         * @method _init_indicator
         * @private
         *
         */
        _init_indicator: function () {
            this.indicator = new Y.bookie.Indicator({
                target: Y.one('.bmarks')
            });
            this.indicator.render();
        },

        /*
         * Fetch a dataset based on our current data
         *
         * @method _fetch_dataset
         * @private
         *
         */
        _fetch_dataset: function () {
            var that = this,
                pager = this.get('pager');

            // make sure we update the api paging information with the latest
            // from our pager
            this.indicator.show();

            this.api.data.count = pager.get('count');
            this.api.data.page = pager.get('page');
            this.api.data.with_content = this.get('with_content');

            this.api.call({
                'success': function (data, request) {
                    var data_node = Y.one('.data_list'),
                        new_nodes = new Y.NodeList();

                    // build models out of our data
                    that.models = new Y.bookie.BmarkList();

                    that.models.add(Y.Array.map(
                        data[that.get('results_key')], function (bmark) {
                            var b = new Y.bookie.Bmark(bmark),
                                n = new Y.bookie.BmarkView({
                                    model: b,
                                    current_user: that.get('current_user'),
                                    resource_user: that.get('resource_user')
                                    }
                                );

                            b.api_cfg = that.get('api_cfg');
                            new_nodes.push(n.render());
                            return b;
                        })
                    );

                    // now set the html
                    data_node.setContent(new_nodes);

                    // update the pagers
                    that._update_pagerview();

                    // finally stop the indicator from spinny spinny
                    that.indicator.hide();
               }
           });
        },

        /**
         * Increment the pager and fetch the next results from the last call.
         *
         * @method _next_page
         * @param {Event} e
         * @private
         *
         */
        _next_page: function (e) {
            var pager = this.get('pager');
            pager.next();

            // now that we've incremented the page let's fetch a new set of
            // results
            this._fetch_dataset();
        },

        /**
         * Update the html reprensenting our Pager information after loading a
         * dataset. For instance, should we hide the prev control if we're
         * onthe first page of results? If we're on last page should we be
         * hiding the next control?
         *
         * @method _update_pagerview
         * @private
         *
         */
        _update_pagerview: function () {
            var pager = this.get('pager');

            // if the current data count is < the pager page count, hide next
            if (this.models.size() < pager.get('count')) {
                 Y.Array.each(this.pagers, function (p) {
                    p.set('show_next', false);
                });
            } else {
                 Y.Array.each(this.pagers, function (p) {
                    p.set('show_next', true);
                });
            }
            // update the pagers
            if (pager.get('page') === 0) {
                // then there is no need for a previous button
                Y.Array.each(this.pagers, function (p) {
                    p.set('show_previous', false);
                });
            } else {
                Y.Array.each(this.pagers, function (p) {
                    p.set('show_previous', true);
                });
            }

            // @todo get rid of this. Changing the showXXX value should fire
            // an event that causes the pagers to re-render themselves, not us
            // manually
            Y.Array.each(this.pagers, function (p) {
                p.render();
            });
        },

        /**
         * Decrement the pager for the current list and fetch a new set of
         * results.
         *
         * @method _prev_page
         * @param {Event} e
         *
         */
        _prev_page: function (e) {
            var pager = this.get('pager'),
                old_page = pager.get('page');

            pager.previous();

            // only update the view if we did change pages (e.g. not on page
            // 1 already)
            if (old_page !== pager.get('page')) {
                // now that we've incremented the page let's fetch a new set
                // of results
                this._fetch_dataset();
            }
        },

        /**
         * Initializer for a class extending Y.Base
         *
         * @method initializer
         * @param {Object} cfg
         * @constructor
         *
         */
        initializer: function (cfg) {
            this.cTemplate = Y.Handlebars.compile(this._get_template());
            this._init_pager();
            this._init_api();
            this._init_indicator();
        },

        /**
         * Build the UI for the result set we've gotten from the API.
         *
         * @method render
         *
         */
        render: function () {
            var that = this,
                // Render this view's HTML into the container element.
                html = this.get('container').set(
                    'innerHTML',
                    this.cTemplate(this.getAttrs())
                );

            // start the request for our models
            this._fetch_dataset();

            var pager_html = html.all('.paging');
            var idx = 0;
            pager_html.each(function (n) {
                var p = that.pagers[idx];
                n.appendChild(p.render());
                idx = idx + 1;
            });
            return html;
        }
    }, {
        ATTRS: {
            /**
             * We're creating a new set of html for our results by getting the
             * container_html.
             *
             * @attribute container
             * @type Y.Node
             *
             */
            container: {
                valueFn: function() {
                    return Y.Node.create(this.container_html);
                }
            },

            /**
             * You need to override this in extending classes that tells the
             * view how to fetch results to put into this view when things
             * like pagers and such change
             *
             * @attribute api_callable
             * @default Api.route.UserBmarksAll
             * @readonly
             *
             */
            api_callable: {
                readonly: true,
                getter: function () {
                    return Y.bookie.Api.route.UserBmarksAll;
                }
            },

            /**
             * @attribute api_cfg
             * @default undefined
             * @type Object
             *
             */
            api_cfg: {

            },

            /**
             * You can add a filter control into the bmark list view. This
             * method is over rideable so that you can figure out how to fetch
             * the filters to apply to the api calls.
             *
             * @attribute filter_control
             * @default ''
             *
             */
            filter_control: {
                value: ''
            },

            /**
             * @attribute pager
             * @default new PagerModel
             * @type PagerModel
             *
             */
            pager: {
                valueFn: function () {
                    return new Y.bookie.PagerModel();
                }
            },

            /**
             * Who is the currently auth'd user
             *
             * @attribute current_user
             * @default undefined
             * @type String
             *
             */
            current_user: {

            },

            /**
             * What is the user that owns this collection
             *
             * e.g. /admin/bmarks == admin user even though I'm not logged in
             * as admin
             *
             * @attribute resource_user
             * @default undefined
             * @type String
             */
            resource_user: {

            },

            /**
             * Where in the results can we find out bmarks?
             *
             * @attribute results_key
             * @readonly
             * @default 'bmarks'
             * @type String
             *
             */
            results_key: {
                value: 'bmarks',
                readonly: true
            },

            /**
             * Should the search view be searching the content of the bookmarks
             * as well?
             *
             * @attribute with_content
             * @default false
             * @type Boolean
             *
             */
            with_content: {
                value: false
            }
        }

    });


    /**
     * Extends BmarkListView to specify a view used for the main /recent pages
     * for displaying lists of bookmarks with a tag control widget tied into
     * the game.
     *
     * @class TagControlBmarkListView
     * @extends BmarkListView
     *
     */
    ns.TagControlBmarkListView = Y.Base.create('tagcontrol-bookie-list-view', ns.BmarkListView, [], {

        /**
         * Standard initializer, note that this ends up being "appended" not
         * replacing the parent's initializer method.
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            // if there are tags added/removed form the TagControl, then make
            // sure we update the list accordingly
            Y.on('tag:changed', this._tags_changed, this);
        },

        /**
         * Handle when tags in the control are changed.
         *
         * @method _tags_changed
         * @param {Event} e
         *
         */
        _tags_changed: function (e) {
            // update the api data with the tags list
            this.api.set('tags', e.tags);

            // update the pager back to page 1
            this.get('pager').set('page', 0);

            // and finally fetch the results
            this._fetch_dataset();
        },
    }, {
        ATTRS: {
            api_callable: {
                readonly: true,
                // then there's a user in our resource path, make the api call a
                // UserBmarksAll vs BmarksAll
                getter: function () {
                    if (this.get('resource_user')) {
                        var cfg = this.get('api_cfg');
                        cfg.resource = this.get('resource_user');
                        this.set('api_cfg', cfg);
                        return Y.bookie.Api.route.UserBmarksAll;
                    } else {
                        return Y.bookie.Api.route.BmarksAll;
                    }
                }
            },

            filter_control: {
                getter: function () {
                    return Y.Handlebars.compile(
                        Y.one('#filter_container').get('text')
                    )({});
                }
            }
        }
    });


    /**
     * Extends BmarkListView to specify a view used for the main /search pages
     * for displaying lists of bookmarks from a search result for the user.
     *
     * @class SearchControlBmarkListView
     * @extends BmarkListView
     *
     */
    ns.SearchingBmarkListView = Y.Base.create('tagcontrol-bookie-list-view', ns.BmarkListView, [], {

        /**
         * Standard initializer, note that this ends up being "appended" not
         * replacing the parent's initializer method.
         *
         * @method initializer
         * @param {Object} cfg
         * @event tag:add Handle a tag:add event so that we can help add it to
         *     the search in question.
         *
         */
        initializer: function (cfg) {
            // if there are tags added/removed form the TagControl, then make
            // sure we update the list accordingly
            Y.one('body').delegate('submit', this._search, 'form#bmark_search', this);

            if (cfg.phrase) {
                this.set('phrase', cfg.phrase.split(' '));
                this.api.set('phrase', this.get('phrase'));
            }

            if (cfg.with_content) {
                this.api.set('with_content', this.get('with_content'));
            }

            // if the tag:add event is fired, then we want to add that tag to
            // our search and reseach
            Y.on('tag:add', function (e) {
                // the tag will be in the event
                var input = Y.one('#search_phrase'),
                    current = Y.one('#search_phrase').get('value');

                input.set('value', [current, e.tag].join(' '));

                // total hack to reuse the _search method
                this._search({preventDefault: function () {}});
            }, this);
        },

        /**
         * Update our result set from a search of the user.
         *
         * @method _search
         * @param {Event} e
         * @private
         *
         */
        _search: function (e) {
            e.preventDefault();
            var phrase = Y.one('#search_phrase').get('value'),
                with_content = Y.one('#with_content');

            // update our data base don the current form information
            this.set('phrase', phrase.split(' '));
            this.set('with_content', with_content.get('checked'));

            // then make sure our api calls are updated with that data
            this.api.set('phrase', this.get('phrase'));
            this.api.set('with_content', this.get('with_content'));

            // update the pager back to page 1
            this.get('pager').set('page', 0);

            // and finally fetch the results
            this._fetch_dataset();
        },
    }, {
        ATTRS: {
            api_callable: {
                readonly: true,

                // then there's a user in our resource path, make the api call a
                // UserBmarksAll vs BmarksAll
                getter: function () {
                    if (this.get('resource_user')) {
                        return Y.bookie.Api.route.UserSearch;
                    } else {
                        return Y.bookie.Api.route.Search;
                    }
                }
            },

            filter_control: {
                getter: function () {
                    var phrase = this.get('phrase');
                    return Y.Handlebars.compile(
                        Y.one('#bmark_search').get('text')
                    )({
                        phrase: phrase ? phrase.join(' ') : '',
                        with_content: this.get('with_content')
                    });
                }
            },

            results_key: {
                value: 'search_results',
                readonly: true
            },

            /**
             * Where is the search form input we're getting input to search
             * against from?
             *
             * @attribute search_form
             * @default '#bmark_search'
             * @type String
             *
             */
            search_form: {
                value: '#bmark_search'
            }
        },
    });


    /**
     * A View for handling representing our paging controls for next/prev
     * pages.
     *
     * @class PagerView
     * @extends Y.View
     *
     */
    ns.PagerView = Y.Base.create('bookie-pager-view', Y.View, [], {
        container_html: '<div class="pager"/>',

        /**
         * Fetch the templates used from the script tags in the html.
         *
         * @method _get_templates
         * @private
         *
         */
        _get_templates: function () {
            return {
                prev: Y.one('#previous_control').get('text'),
                next: Y.one('#next_control').get('text')
            };
        },

        /**
         * Make sure the previous contol is visible to the user.
         *
         * @method _show_previous
         * @param {Event} e
         *
         */
        _show_previous: function (e) {
            var val = e.newVal,
                prev = e.prevVal;

            // make sure we update render
            // but only if the value is different
            if (val && val !== prev) {
                this.render();
            }
        },

        /**
         * Make sure that we display the next control properly.
         *
         * @method _show_next
         * @param {Event} e
         *
         */
        _show_next: function (e) {
            var val = e.newVal,
                prev = e.prevVal;

            // make sure we update render
            // but only if the value is different
            if (val && val !== prev) {
                this.render();
            }
        },

        /**
         * @attribute events
         * @default Object
         *
         */
        events: {
            '.previous': {
                click: 'previous_page'
            },
            '.next': {
                click: 'next_page'
            }
        },

        /**
         * Basic initializer
         *
         * @method initializer
         * @param {Object} cfg
         * @event show_previousChange
         * @event show_nextChange
         *
         */
        initializer: function (cfg) {
            var tpl = this._get_templates();
            this.cPrevTemplate = Y.Handlebars.compile(tpl.prev);
            this.cNextTemplate = Y.Handlebars.compile(tpl.next);

            this.after('show_previousChange', this._show_previous, this);
            this.after('show_nextChange', this._show_next, this);
        },

        /**
         * Handle the previous page clicked event.
         *
         * @method previous_page
         * @param {Event} e
         *
         */
        previous_page: function (e) {
            e.preventDefault();
            Y.fire(this.get('previous_event'));
        },

        /**
         * Handle the next page clicked event.
         *
         * @method next_page
         * @param {Event} e
         *
         */
        next_page: function (e) {
            e.preventDefault();
            Y.fire(this.get('next_event'));
        },

        /**
         * render out the control to the container specified.
         *
         * @method render
         * @return {String} generated html
         *
         */
        render: function () {
            // Render this view's HTML into the container element.
            return this.get('container').set(
                'innerHTML',
                this.cPrevTemplate(this.getAttrs()) +
                    this.cNextTemplate(this.getAttrs())
            );
        }

    }, {
        ATTRS: {
            /**
             * @attribute container
             * @default Y.Node
             * @type Y.Node
             *
             */
            container: {
                valueFn: function () {
                    return Y.Node.create(this.container_html);
                }
            },

            /**
             * @attribute id
             * @default 'pager'
             * @type String
             *
             */
            id: {
                value: 'pager'
            },

            /**
             * @attribute previous_event
             * @default '$id:previous'
             * @type String
             * @readonly
             *
             */
            previous_event: {
                readOnly: true,
                valueFn: function () {
                    return this.get('id') + ':previous';
                }
            },

            /**
             * @attribute next_event
             * @default '$id:next'
             * @type String
             * @readonly
             *
             */
            next_event: {
                readOnly: true,
                valueFn: function () {
                    return this.get('id') + ':next';
                }
            },

            /**
             * By default we don't need a previous usually on initial page
             * load
             *
             * @attribute show_previous
             * @default false
             * @type Boolean
             *
             */
            show_previous: {
                value: false
            },

            /**
             * @attribute show_next
             * @default true
             * @type Boolean
             *
             */
            show_next: {
                value: true
            }
        }
    });


    /**
     * This is the view for a single bookmark in a result set. It handles its
     * own events and rendering/updating and this is where the remove event
     * from the UI gets captured and passed along to the bound model.
     *
     * @class BmarkView
     * @extends Y.View
     *
     */
    ns.BmarkView = Y.Base.create('bookie-bmark-view', Y.View, [], {
        container_html: '<div class="bmark"/>',

        /**
         * Get the template string used to render this view.
         *
         * @method _get_template
         * @private
         *
         */
        _get_template: function () {
            return Y.one('#bmark_row').get('text');
        },

        /**
         * If you click on a tag in the bookmark view filter the page to just
         * that tag.
         *
         * @method _tag_filter
         * @private
         *
         */
        _tag_filter: function (e) {
            e.preventDefault();
            // find the tag we need to pass in the event
            Y.fire('tag:add', {tag: e.currentTarget.get('text')});
        },

        events: {
            '.delete': {
                click: 'remove'
            },
            '.tag': {
                click: '_tag_filter'
            }
        },

        /**
         * General initializer method.
         *
         * @method intializer
         * @param {Object} cfg
         * @constructor
         *
         */
        initializer: function (cfg) {
            this.cTemplate = Y.Handlebars.compile(this._get_template());
        },

        /**
         * Handle the remove event on this bookmark
         *
         * @method remove
         *
         */
        remove: function () {
            var that = this;
            this.get('model').remove();

            this.get('container').transition({
                easing: 'ease',
                duration: 0.4,
                opacity: 0
            }, function () {
                that.destroy();
            });
        },

        /**
         * Render out html for this bookmark based on the model data.
         *
         * @method render
         * @return Y.Node
         *
         */
        render: function () {
            // Render this view's HTML into the container element.
            var tpl_data = this.get('model').getAttrs();
            tpl_data.owner = this.get('current_user') == this.get('model').get('username');

            return this.get('container').set(
                'innerHTML',
                this.cTemplate(tpl_data)
            );
        }
    }, {
        ATTRS: {
            /**
             *
             * The view is for a url of a specific user.
             *
             * Say /admin/bmarks for the admin bookmarks, does not mean I'm
             * the admin.
             *
             * @attribute resource_user
             * @default undefined
             * @type String
             *
             */
            resource_user: {
            },

            /**
             * The current authorized user.
             *
             * @attribute current_user
             * @default undefined
             * @type String
             *
             */
            current_user: {
            },

            /**
             * Each view is rendered into a container node that's then
             * returned via the render method.
             *
             * @attribute container
             * @default Y.Node
             * @type Y.Node
             * @readonly
             *
             */
            container: {
                valueFn: function () {
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


    /**
     * Generate the html view for a User's account
     *
     * @class AccountView
     * @extends Y.View
     *
     */
    ns.AccountView = Y.Base.create('bookie-account-view', Y.View, [], {
        _blet_visible: false,
        _api_visibile: false,

        /**
         * Bind all events for this html view.
         *
         * @method _bind
         *
         */
        _bind: function () {
            Y.one('#show_key').on(
                'click',
                this._show_api_key,
                this
            );
            Y.one('#show_bookmarklet').on(
                'click',
                this._show_bookmarklet,
                this
            );
        },

        /**
         * Handle displaying the API key for a user. This requires making an
         * API request since we don't dump the API key by default into the
         * page html to help prevent it leaking out.
         *
         * @method _show_api_key
         * @param {Event} e
         *
         */
        _show_api_key: function (e) {
            var key_div = Y.one('#api_key'),
                key_container = Y.one('#api_key_container');

            e.preventDefault();

            // if the api key is showing and they click this, hide it
            if(this._api_visible) {
                key_container.hide(true);
                this._api_visible = false;
            } else {
                var api = new Y.bookie.Api.route.UserApiKey(this.get('api_cfg'));
                this._api_visible = true;
                // make an ajax request to get the api key for this user and then
                // show it in the container for it
                api.call({
                    success: function (data, request) {
                        key_div.setContent(data.api_key);
                        key_container.show(true);
                    }

                });
            }
        },

        /**
         * Handle displaying the bookmarklet information when the user
         * requests it.
         *
         * @method _show_bookmarklet
         * @param {Event} e
         *
         */
        _show_bookmarklet: function (e) {
            var blet = Y.one('#bookmarklet_text');
            e.preventDefault();

            // if the api key is showing and they click this, hide it
            // the opacity must start out at 0 for the transition to take
            // effect
            if(this._blet_visible) {
                this._blet_visible = false;
                blet.hide(true);
            } else {
                this._blet_visible = true;
                blet.show(true);
            }
        },

        /**
         * General initializer
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            this._bind();

            // setup the password view
            // it needs the api cfg for updating the password via the api
            this.password = new ns.PasswordView({
                api_cfg: this.get('api_cfg')
            });
            this.account_info = new ns.AccountInfoView({
                api_cfg: this.get('api_cfg')
            });
        }

    }, {
        ATTRS: {
            /**
             * @attribute api_cfg
             * @default undefined
             * @type Object
             *
             */
            api_cfg: {
                required: true
            }
        }
    });


    /**
     * Handle the display of the password reset view.
     *
     * @class PasswordView
     * @extends Y.View
     *
     */
    ns.PasswordView = Y.Base.create('bookie-password-view', Y.View, [], {
        _visible: false,

        /**
         * Bind all events thats the UI needs to function.
         *
         * @method _bind
         * @private
         *
         */
        _bind: function () {
            Y.one('#show_password').on(
                'click',
                this._show_password,
                this
            );
            Y.one('form#password_reset').on(
                'submit',
                this._change_password,
                this
            );
            Y.one('#submit_password_change').on(
                'click',
                this._change_password,
                this
            );
        },

        /**
         * Handle changing the password via an API call.
         *
         * @method _change_password
         * @param {Event} e
         * @private
         *
         */
        _change_password: function (e) {
            var that = this,
                api_cfg = this.get('api_cfg');

            e.preventDefault();

            // hide the current message window
            Y.one('#password_msg').hide();

            // add the password data to the cfg passed to the api
            api_cfg = Y.merge(api_cfg, {
                current_password: Y.one('#current_password').get('value'),
                new_password: Y.one('#new_password').get('value')
            });

            var api = new Y.bookie.Api.route.UserPasswordChange(api_cfg);
            api.call({
                success: function (data, request) {
                    that._show_message(data.message, true);
                    that._reset_password();
                },
                error: function (data, status_str, response, arguments) {
                    that._show_message(data.error, false);
                    that._reset_password();
                }
            });
        },


        /**
         * Reset the form once we've successfully completed an an attempt to
         * change the password.
         *
         * @method _reset_password
         *
         */
        _reset_password: function () {
            Y.one('#current_password').set('value', '');
            Y.one('#new_password').set('value', '');
            Y.one('#password_change').hide(true);

            // make sure we keep visible in sync
            this._visible = false;
        },

        /**
         * Display any message based on if the request to change is successful
         * or ended in error.
         *
         * @method _show_message
         * @param {String} msg
         * @param {Boolean} success
         *
         */
        _show_message: function (msg, success) {
            var msg_div = Y.one('#password_msg');
            msg_div.setContent(msg);

            if (success) {
                msg_div.replaceClass('error', 'success');
            } else {
                msg_div.replaceClass('success', 'error');
            }

            msg_div.show(true);
        },

        /**
         * Show the password change component.
         *
         * @method _show_password
         * @param {Event} e
         *
         */
        _show_password: function (e) {
            var pass_div = Y.one('#password_change');
            e.preventDefault();

            // if the api key is showing and they click this, hide it
            if(this._visible) {
                pass_div.hide(true);
                this._visible = false;
            } else {
                this._visible = true;
                pass_div.show(true);
            }
        },


        /**
         * General initializer
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            this._bind();
        }

    }, {
        ATTRS: {
            /**
             * @attribute api_cfg
             * @default undefined
             * @type Object
             *
             */
            api_cfg: {
                required: true
            }
        }
    });


    /**
     * Handle the view ofr the account information. This is for changing the
     * user's name, email, etc.
     *
     * @class AccountInfoView
     * @extends Y.View
     *
     */
    ns.AccountInfoView = Y.Base.create('bookie-account-info-view', Y.View, [], {
        /**
         * Bind all UI events for the UI.
         *
         * @method _bind
         * @private
         *
         */
        _bind: function () {
            Y.one('#submit_account_change').on(
                'click',
                this._update_account,
                this
            );
        },

        /**
         * Handle submitting the API to update the user's account information.
         *
         * @method _update_account
         * @param {Event} e
         * @private
         *
         */
        _update_account: function (e) {
            var that = this,
                api_cfg = this.get('api_cfg');

            e.preventDefault();
            Y.one('#account_msg').hide();

            // add the password data to the cfg passed to the api
            api_cfg = Y.merge(api_cfg, {
                name: Y.one('#name').get('value'),
                email: Y.one('#email').get('value')
            });

            var api = new Y.bookie.Api.route.UserAccountChange(api_cfg);
            api.call({
                success: function (data, request) {
                    that._show_message('Account updated...', true);
                },
                error: function (data, status_str, response, arguments) {
                    console.log(data);
                    console.log(response);
                }
            });
        },

        /**
         * Handle showing the user any success for failure messages based on
         * the result of an attempt to update the user's account information.
         *
         * @method _show_message
         * @param {String} msg
         * @param {Boolean} success
         *
         */
        _show_message: function (msg, success) {
            var msg_div = Y.one('#account_msg');
            msg_div.setContent(msg);

            if (success) {
                msg_div.replaceClass('error', 'success');
            } else {
                msg_div.replaceClass('success', 'error');
            }

            msg_div.show(true);
        },

        /**
         * General initializer
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            this._bind();
        }
    }, {
        ATTRS: {
            /**
             * @attribute api_cfg
             * @default undefined
             * @type Object
             *
             */
            api_cfg: {
                required: true
            }
        }
    });


    /**
     * Handle the UI for the login view.
     *
     * @class LoginView
     * @extends Y.View
     *
     */
    ns.LoginView = Y.Base.create('bookie-login-view', Y.View, [], {
        _visible: false,

        /**
         * Bind all of the UI events for this html view.
         *
         * @method _bind
         * @private
         *
         */
        _bind: function () {
            Y.one('#show_forgotten').on(
                'click',
                this._show_forgotten,
                this
            );
            Y.one('#submit_forgotten').on(
                'click',
                this._forgotten,
                this
            );

        },

        /**
         * Clear out the login form.
         *
         * @method _clear
         * @private
         *
         */
        _clear: function () {
            Y.one('#email').set('value', '');
        },

        /**
         * Show the forgotten password UI box for the user to use.
         *
         * @method _show_forgotten
         * @param {Event} e
         * @private
         *
         */
        _show_forgotten: function (e) {
            var pass_div = Y.one('#forgotten_password');
            e.preventDefault();

            // if the api key is showing and they click this, hide it
            if(this._visible) {
                pass_div.hide(true);
                this._visible = false;
            } else {
                this._visible = true;
                pass_div.show(true);
            }
        },

        /**
         * Handle a user submitting the form to reset their account because
         * they've forgotten the information.
         *
         * @method _forgotten
         * @param {Event} e
         * @private
         *
         */
        _forgotten: function (e) {
            var that = this,
                api_cfg = this.get('api_cfg');

            e.preventDefault();

            // hide the current message window
            Y.one('#forgotten_msg').hide();

            // add the password data to the cfg passed to the api
            api_cfg = Y.merge(api_cfg, {
                email: Y.one('#email').get('value')
            });

            var api = new Y.bookie.Api.route.SuspendUser(api_cfg);
            api.call({
                success: function (data, request) {
                    that._clear();
                    that._show_message(data.message, true);
                },
                error: function (data, status_str, response, arguments) {
                    console.log(data);
                    console.log(response);
                }
            });
        },

        /**
         * Handle displaying success and failure messages to the user when
         * they submit the forgotten login information request.
         *
         * @method _show_message
         * @param {String} msg
         * @param {Boolean} success
         *
         */
        _show_message: function (msg, success) {
            var msg_div = Y.one('#forgotten_msg');
            msg_div.setContent(msg);

            if (success) {
                msg_div.replaceClass('error', 'success');
            } else {
                msg_div.replaceClass('success', 'error');
            }

            msg_div.show(true);
        },

        /**
         * General initializer
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            this._bind();
        }
    }, {
        ATTRS: {
            /**
             * @attribute api_cfg
             * @default undefined
             * @type Object
             *
             */
            api_cfg: {
                required: true
            }
        }
    });


    /**
     * Handle the UI for the user resetting of their account after it's been
     * deactivated.
     *
     * @class AccountResetView
     * @extends Y.View
     *
     */
    ns.AccountResetView = Y.Base.create('bookie-account-reset-view', Y.View, [], {
        /**
         * Bind the UI events for this html view.
         *
         * @method _bind
         * @private
         *
         */
        _bind: function () {
            Y.one('#submit_password_change').on(
                'click',
                this._account_reset,
                this
            );
            Y.one('#password_reset').on(
                'submit',
                this._account_reset,
                this
            );
        },

        /**
         * Handle the API request to unlock the user's account so they can use
         * it again.
         *
         * @method _account_reset
         * @param {Event} e
         *
         */
        _account_reset: function (e) {
            var that = this,
                api_cfg = this.get('api_cfg');

            e.preventDefault();

            // hide the current message window
            Y.one('#password_msg').hide();

            // add the password data to the cfg passed to the api
            api_cfg = Y.merge(api_cfg, {
                username: Y.one('#username').get('value'),
                code: Y.one('#code').get('value'),
                password: Y.one('#new_password').get('value')
            });

            var api = new Y.bookie.Api.route.UnSuspendUser(api_cfg);
            api.call({
                success: function (data, request) {
                    that._show_message(data.message, true);
                },
                error: function (data, status_str, response, arguments) {
                    that._show_message(data.error, false);
                    console.log(data);
                    console.log(response);
                }
            });
        },

        /**
         * Handle displaying the success and faliure messages to the user
         * based on the response of the API request.
         *
         * @method _show_message
         * @param {String} msg
         * @param {Boolean} success
         *
         */
        _show_message: function (msg, success) {
            var msg_div = Y.one('#password_msg');
            msg_div.setContent(msg);

            if (success) {
                msg_div.replaceClass('error', 'success');
            } else {
                msg_div.replaceClass('success', 'error');
            }

            msg_div.show(true);
        },

        /**
         * General initializer method.
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            this._bind();
        }
    }, {
        ATTRS: {
            /**
             * @attribute api_cfg
             * @default undefined
             * @type Object
             *
             */
            api_cfg: {
                required: true
            }
        }
    });

    /**
     * View control for the options html pane in the extension.
     *
     * @class OptionsView
     * @extends Y.View
     *
     */
    ns.OptionsView = Y.Base.create('bookie-options-view', Y.View, [], {
        /**
         * Setup the options form with data from our model to start out with.
         *
         * @method _init_form
         * @private
         *
         */
        _init_form: function () {
            var opts = this.get('model');

            Y.one('#api_url').set('value', opts.get('api_url'));
            Y.one('#api_username').set('value', opts.get('api_username'));
            Y.one('#api_key').set('value', opts.get('api_key'));

            if (opts.get('cache_content') === 'true') {
                Y.one('#cache_content').set('checked', true);
            } else {
                Y.one('#cache_content').set('checked', false);
            }
        },

        /**
         * Display any message based on if the request to change is successful
         * or ended in error.
         *
         * @method _show_message
         * @param {String} msg
         * @param {Boolean} success
         *
         */
        _show_message: function (msg, success) {
            var msg_div = Y.one('#options_msg');
            msg_div.setContent(msg);

            if (success) {
                msg_div.replaceClass('error', 'success');
            } else {
                msg_div.replaceClass('success', 'error');
            }

            msg_div.show(true);
        },

        /**
         * Perform a sync of the bookmarks they user has stored by requesting
         * the list of hashes from the API on the server.
         *
         * @method _sync_bookmarks
         * @param {Event} e
         *
         */
        _sync_bookmarks: function (e) {
            var opts = this.get('model');
            var ind = new Y.bookie.Indicator({
                target: Y.one('#sync')
            });
            ind.render();
            ind.show();

            var api = new Y.bookie.Api.route.Sync({
                url: opts.get('api_url') + '/api/v1',
                username: opts.get('api_username'),
                api_key: opts.get('api_key')
            });

            // make the api calls
            api.call({
                'success': function (data, request) {
                    Y.Array.each(data.hash_list, function (h) {
                        // write out each hash to localStorage
                        localStorage.setItem(h, 'true');
                    });

                    // finally stop the indicator from spinny spinny
                    ind.hide();
                }
            });
        },

        /**
         * Handle dispatching events for the UI.
         *
         * @attribute events
         * @type Object
         *
         *
         */
        events: {
            // @event #form:submit
            'form#form': {
                'submit': 'update_options'
            },
            '#sync_button': {
                'click': '_sync_bookmarks'
            }
        },

        template: '',

        /**
         * General initializer method.
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {
            this._init_form();
        },


        /**
         * Handle updating the options model with our selected information
         * whenthe form is submitted.
         *
         * @method update_options
         * @param {Event} e
         *
         */
        update_options: function (e) {
            e.preventDefault();

            var msg_div = Y.one('#options_msg');
            msg_div.hide();

            var opts = this.get('model');
            // fetch the new values from the form and then update our model
            // with them.
            opts.set('api_url', Y.one('#api_url').get('value'));
            opts.set('api_username', Y.one('#api_username').get('value'));
            opts.set('api_key', Y.one('#api_key').get('value'));

            if (Y.one('#cache_content').get('checked')) {
                opts.set('cache_content', 'true');
            } else {
                opts.set('cache_content', 'false');
            }

            // one updated, now save it
            opts.save()
            this._show_message('Saved your settings...', true);
        }
    }, {
        ATTRS: {
            /**
             * @attribute container
             * @default Y.Node the body of the document
             * @type Y.Node
             *
             */
            container: {
                valueFn: function () {
                    return Y.one('body');
                }
            },

            /**
             * @attribute model
             * @default Y.bookie.OptionModel
             * @type Y.bookie.OptionModel
             *
             */
            model: {
                valueFn: function () {
                    return new Y.bookie.OptionsModel();
                }
            }
        }
    });

}, '0.1.0', { requires: ['base',
    'view', 'bookie-model', 'bookie-api', 'bookie-indicator', 'handlebars', 'transition',
    'bookie-tagcontrol', 'substitute']
});
