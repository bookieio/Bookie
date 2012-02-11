YUI().add('bookie-chrome', function (Y) {
    var ns = Y.namespace('bookie');

    ns.ChromePopup = Y.Base.create('bookie-chrome-view', Y.View, [], {

        /**
         * Process deleting a bookmark requested by the extension.
         *
         * @method _handle_delete
         * @param {Event} e
         *
         */
        _handle_delete: function (e) {

        },

        /**
         * Process storing a bookmark via the API.
         *
         * @method _handle_submit
         * @param {Event} e
         *
         */
        _handle_submit: function (e) {

        },

        events: {
            'form#form': {
                submit: '_handle_submit'
            },
            '#delete': {
                'click': '_handle_delete'
            }
        },

        /**
         * Standard initializer, prep up the popup for use.
         *
         * @method initializer
         * @param {Object} cfg
         *
         */
        initializer: function (cfg) {

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
                    return new Y.bookie.Bmark();
                }
            }


        }
    });

    ns.Chrome = Y.Base.create('bookie-chrome-popup', Y.Base, [], {

        _init_popup: function () {
            // bind up the TagControl to get that UI flash over with asap
            var tagcontrol = new Y.bookie.TagControl({
               api_cfg: api_cfg,
               srcNode: Y.one('#tag_filter'),
               initial_tags: tags
            });
            tagcontrol.render();

            // input with the tag plugin version
            Y.one('div.yui3-bookie-tagcontrol input').focus();

            Y.one('#form').on('submit', this.save, this);
            this.init_form_data('chrome-extension');

            /**
             * Load the data for the current page in case we've got data on it
             *
             */
            var api_cfg = this.settings.getAttrs();
            api_cfg.hash_id = hash_url(this.bookmark.url);
            var api = new Y.bookie.Api.route.Bmark(API_CFG);

            api.call({
                success: function (data, request) {

                },
                error: function (data, status_str, response) {

                }
            });

            // $($b.EVENTID).trigger($b.events.LOAD, current_tab_info);

            /**
             *
             * @todo
             * This is all about setting up the suggested tags for use. We
             * need to bind click events, etc when used. We'll add that back
             * in later
             *
             */
            // $($b.EVENTID).bind($b.events.DUPE_TAGS, $b.ui.dupe_tags);
            // $('#latest_tags').delegate('a', 'click', function (ev) {
            //     ev.preventDefault();
            //     $b.ui.dupe_tags($(this));
            // });
        },

        /**
         * We need to fill in a bunch of our form data in order to be able to
         * move forward with things
         *
         * @param inserted_by string for how this is getting saved, the toread
         * right click option, the chrome extension itself, etc?
         *
         */
        init_form_data: function (inserted_by) {
            Y.one('#url').set('value', this.bookmark.url);
            Y.one('#description').set('value', this.bookmark.description);
            Y.one('#inserted_by').set('value', inserted_by);
            Y.one('#extended').set('value', "");
            console.log('populating form base');
        },

        _setup_readable_content: function () {
            // don't worry about loading the content of the page if we
            // don't have it set in our options
            if(!localStorage['cache_content'] || localStorage['cache_content'] != "true") {
                // then skip it, we don't want the added load on the
                // browser or the server
            } else {
                bkg = chrome.extension.getBackgroundPage();

                bkg.inject_readable(function () {
                    Y.one('#content').set('value', bkg.get_html_content());
                });
            }

        },

        initializer: function (cfg) {
            this.settings = new ns.Settings();
            this.bookmark = new Y.bookie.Bmark(cfg.url_data);

            // we can only go on if the settings are ok
            if (!this.valid_settings()) {
                // the errors are displayed by the error code, yea this should
                // be split out I know...but time heals all code wounds
                // right?...right?
                return;
            } else {
                // now let's bind up the popup and make it all work
                this._init_popup();
                this._setup_readable_content();
            }
        },

        valid_settings = function () {
            var errors = new ns.PopupErrors();

            settings = this.settings;

            var required = [
                'api_url',
                'api_username',
                'api_key'
            ];

            Y.Array.each(required, function (key) {
                if (!setting.get(key)) {
                    errors.add("The value for " + key + " has not been set");
                }
            });

            // display errors if we have them
            if (errors.length) {
                errors.render();
                return false;
            } else {
                return true;
            }
        },
    }, {
        ATTRS: {
            /**
             * When we init we want to tell the chrome extension about the
             * current url. It's passed into via this url data from the chrome
             * extension api that has the url and title of the current page
             *
             */
            url_data: {},
        }
    });


    ns.Settings = Y.Base.create('bookie-chrome-settings', Y.Model, [], {
        _bind_events: function () {
            var that = this;
            // if any attrs are changed we want to write them out to
            // localstorage
            this.on('change', function (e) {
                that.write_settings();
            });

        },

        _load_settings: {
            this.set('api_url', localStorage.getItem('api_url'));
            this.set('api_username', localStorage.getItem('api_username'));
            this.set('api_key', localStorage.getItem('api_key'));
        },

        write_settings: {
            localStorage.setItem('api_url', this.get('api_url'));
            localStorage.setItem('api_username', this.get('api_username'));
            localStorage.setItem('api_key', this.get('api_key'));
        },

        initialize: function (cfg) {
            // to start out, load the current settings
            this._load_settings();

            // only bind after we've loaded to prevent change events from
            // initial load hitting
            this._bind_events();
        }

    }, {
        ATTRS: {
            /**
             * We can only have one instance of settings, it's id is always 1
             */
            id: {
                value: 1
            },

            api_url: {

            },

            api_username: {

            },

            api_key: {

            },

            cache_content: {

            }
        }
    }),

    ns.PopupErrors = Y.Base.create('bookie-chrome-errors', Y.Base, [], {
        add: function (error_msg) {
            this.get('errors').push(error_msg);
        },

        clear: function () {
            this.set('errors', []);
            this.get('target_node').setContent('');
        },

        render: function () {
            var errors = this.get('errors');

            if(errors.length) {
                var error_nodes = new Y.NodeList();

                Y.Array.each(function (msg) {
                    var n = Y.Node.create('<li/>');
                    n.set('text', msg);
                    error_nodes.push(n);
                });

                this.get('target_node').setContent(error_nodes);
            }
        }
    }, {
        ATTRS: {
            errors: {
                value: []
            },

            length: {
                getter: function () {
                    return this.get('errors').length;
                }
            }

            target_node: {
                valueFn: function () {
                    return Y.one('#errors');
                }
            }
        }
    });


    ns.ChromeNotification = Y.Base.create('bookie-chrome-notification',
        Y.Base, [], {




        }, {
            ATTRS: {
                code: {},
                type: {},
                short_text: {},
                longtext: {},
            }
        }
    );


    ns.ChromeBadge = Y.Base.create('bookie-chrome-badge', Y.Base, [], {
        // colors must be defined in the RGBA syntax for the chrome api to work
        _colors: {
            'green': [15, 232, 12, 255],
            'red':   [200, 50, 50, 255],
            'blue':  [0, 191, 255, 255]
        },

        _clear: function (ms) {
            var ttl = ms || 0;
            window.setTimeout(function() {
                chrome.browserAction.setBadgeText({text: ''});
            }, ttl);
        },

        _set: function (text, bgcolor) {
            if (bgcolor) {
                chrome.browserAction.setBadgeBackgroundColor({color: bgcolor});
            }

            chrome.browserAction.setBadgeText({text: text});

            this.clear(this.get('time'));
        },

        initializer: function () {},

        show: function (notification) {
            var color,
                badge;

            switch(notification.type) {
                case "error":
                    color = "red";
                    badge = "Err";
                    break;
                case "info":
                    color = "green";
                    badge = "Ok";
                    break;
                default:
                    console.log("Unknown notification type: " + \
                                notification.type);
            }

            // add a notice to the badge as necessary
            this._set(badge, this.get('time'), this._colors[color]);
        }
    }, {
        ATTRS: {
            color: {},
            text: {},
            time: {
                // length to show the badge in ms
                value: 5000
            }

        }
    });


}, '0.1', {
    requires: ['base', 'event', 'node', 'bookie-model']
});
