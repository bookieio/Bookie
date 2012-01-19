/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */
YUI.add('bookie-view', function (Y) {
    var _ = Y.Lang.substitute,
        ns = Y.namespace('bookie');

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
         */
        _init_api: function () {
            var api_callable = this.get('api_callable');
            this.api = new api_callable(this.get('api_cfg'));
        },

        /*
         * Fetch a dataset based on our current data
         *
         */
        _fetch_dataset: function () {
            var that = this,
                pager = this.get('pager');

            // make sure we update the api paging information with the latest
            // from our pager

            this.api.data.count = pager.get('count');
            this.api.data.page = pager.get('page');
            this.api.data.with_content = pager.get('with_content');

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
               }
           });
        },

        _next_page: function (e) {
            var pager = this.get('pager');
            pager.next();

            // now that we've incremented the page let's fetch a new set of
            // results
            this._fetch_dataset();
        },

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
         * Need to make some updates to the ui based on the current page
         *
         */
        _update_ui: function () {

        },

        initializer: function (cfg) {
            this.cTemplate = Y.Handlebars.compile(this._get_template());
            this._init_pager();
            this._init_api();
        },

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
             */
            api_callable: {
                readonly: true,
                getter: function () {
                    return Y.bookie.Api.route.UserBmarksAll;
                }
            },

            api_cfg: {

            },

            /**
             * You can add a filter control into the bmark list view
             *
             */
            filter_control: {
                value: ''
            },

            pager: {
                valueFn: function () {
                    return new Y.bookie.PagerModel();
                }
            },

            /**
             * Who is the currently auth'd user
             *
             */
            current_user: {

            },

            /**
             * What is the user that owns this collection
             *
             * e.g. /admin/bmarks == admin user even though I'm not logged in
             * as admin
             */
            resource_user: {

            },

            /**
             * Where in the results can we find out bmarks?
             *
             */
            results_key: {
                value: 'bmarks',
                readonly: true
            }
        }

    });


    ns.TagControlBmarkListView = Y.Base.create('tagcontrol-bookie-list-view', ns.BmarkListView, [], {
        initializer: function (cfg) {
            // if there are tags added/removed form the TagControl, then make
            // sure we update the list accordingly
            Y.on('tag:changed', this._tags_changed, this);
        },

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

    ns.SearchingBmarkListView = Y.Base.create('tagcontrol-bookie-list-view', ns.BmarkListView, [], {
        initializer: function (cfg) {
            // if there are tags added/removed form the TagControl, then make
            // sure we update the list accordingly
            Y.delegate('submit', this._search, '#search_form', this);

            if (cfg.phrase) {
                this.set('phrase', cfg.phrase.split(' '));
                this.api.set('phrase', this.get('phrase'));
            }
        },

        _search: function (e) {
            // find out what our search phrase is and if we've checked the
            // full content search option, then make the call and let's roll.

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
                        return Y.bookie.Api.route.Search;
                    } else {
                        return Y.bookie.Api.route.UserSearch;
                    }
                }
            },

            filter_control: {
                getter: function () {
                    var phrase = this.get('phrase');
                    return Y.Handlebars.compile(
                        Y.one('#bmark_search').get('text')
                    )({
                        phrase: phrase ? phrase.join(' ') : ''
                    });
                }
            },

            /**
             * Where in the results can we find out bmarks?
             *
             */
            results_key: {
                value: 'search_results',
                readonly: true
            },

            search_form: {
                value: '#bmark_search'
            }
        },
    });


    ns.PagerView = Y.Base.create('bookie-pager-view', Y.View, [], {
        container_html: '<div class="pager"/>',

        _get_templates: function () {
            return {
                prev: Y.one('#previous_control').get('text'),
                next: Y.one('#next_control').get('text')
            };
        },

        _show_previous: function (e) {
            var val = e.newVal,
                prev = e.prevVal;

            // make sure we update render
            // but only if the value is different
            if (val && val !== prev) {
                this.render();
            }
        },

        _show_next: function (e) {
            var val = e.newVal,
                prev = e.prevVal;

            // make sure we update render
            // but only if the value is different
            if (val && val !== prev) {
                this.render();
            }
        },

        events: {
            '.previous': {
                click: 'previous_page'
            },
            '.next': {
                click: 'next_page'
            }
        },

        initializer: function (cfg) {
            var tpl = this._get_templates();
            this.cPrevTemplate = Y.Handlebars.compile(tpl.prev);
            this.cNextTemplate = Y.Handlebars.compile(tpl.next);

            this.after('show_previousChange', this._show_previous, this);
            this.after('show_nextChange', this._show_next, this);
        },

        previous_page: function (e) {
            e.preventDefault();
            Y.fire(this.get('previous_event'));
        },

        next_page: function (e) {
            e.preventDefault();
            Y.fire(this.get('next_event'));
        },

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
            container: {
                valueFn: function () {
                    return Y.Node.create(this.container_html);
                }

            },

            id: {
                value: 'pager'
            },

            previous_event: {
                readOnly: true,
                valueFn: function () {
                    return this.get('id') + ':previous';
                }
            },

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
             */
            show_previous: {
                value: false
            },

            show_next: {
                value: true
            }
        }
    });


    ns.BmarkView = Y.Base.create('bookie-bmark-view', Y.View, [], {
        container_html: '<div class="bmark"/>',

        _get_template: function () {
            return Y.one('#bmark_row').get('text');
        },

        events: {
            '.delete': {
                click: 'remove'
            }
        },

        initializer: function (cfg) {
            this.cTemplate = Y.Handlebars.compile(this._get_template());
        },

        /**
         * Handle the remove event on this bookmark
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


    ns.AccountView = Y.Base.create('bookie-account-view', Y.View, [], {
        _blet_visible: false,
        _api_visibile: false,

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
            api_cfg: {
                required: true
            }
        }
    });


    ns.PasswordView = Y.Base.create('bookie-password-view', Y.View, [], {
        _visible: false,

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

        _reset_password: function () {
            Y.one('#current_password').set('value', '');
            Y.one('#new_password').set('value', '');
            Y.one('#password_change').hide(true);

            // make sure we keep visible in sync
            this._visible = false;
        },

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

        initializer: function (cfg) {
            this._bind();
        }

    }, {
        ATTRS: {
            api_cfg: {
                required: true
            }
        }
    });


    ns.AccountInfoView = Y.Base.create('bookie-account-info-view', Y.View, [], {
        _bind: function () {
            Y.one('#submit_account_change').on(
                'click',
                this._update_account,
                this
            );
        },

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

        initializer: function (cfg) {
            this._bind();
        }
    }, {
        ATTRS: {
            api_cfg: {
                required: true
            }
        }
    });


    ns.LoginView = Y.Base.create('bookie-login-view', Y.View, [], {
        _visible: false,

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

        _clear: function () {
            Y.one('#email').set('value', '');
        },

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

        initializer: function (cfg) {
            this._bind();
        }
    }, {
        ATTRS: {
            api_cfg: {
                required: true
            }
        }
    });


    ns.AccountResetView = Y.Base.create('bookie-account-reset-view', Y.View, [], {
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

        initializer: function (cfg) {
            this._bind();
        }
    }, {
        ATTRS: {
            api_cfg: {
                required: true
            }
        }
    });
}, '0.1.0', { requires: ['base',
    'view', 'bookie-model', 'bookie-api', 'handlebars', 'transition',
    'bookie-tagcontrol']
});
