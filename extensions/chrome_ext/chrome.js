YUI().add('bookie-chrome', function (Y) {
    var ns = Y.namespace('bookie.chrome');

    ns.Popup = Y.Base.create('bookie-chrome-view', Y.View, [], {
        /**
         * We start out with an empty model from the extension and we need to
         * check if there's information on this bookmark on the server and if
         * so update the bookmark model.
         *
         * @method _fetch_model
         *
         */
        _fetch_model: function () {

        },

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
        _handle_save: function (e) {

        },

        /**
         * Bind the model up with the form and display it's values into the
         * fields.
         *
         * @method _init_form
         *
         */
        _init_form: function () {
            // update the fields with model data
            Y.one('#url').set('value', this.get('model').get('url'));
            Y.one('#description').set('value', this.get('model').get('description'));
            Y.one('#tag_filter').set('value', this.get('model').get('tag_str'));
            Y.one('#extended').set('value', this.get('model').get('extended'));
            Y.one('#inserted_by').set('value', 'chrome_ext');

            // make the tag field a TagControl
            this.tag_controller = new Y.bookie.TagControl({
                api_cfg: this.api_cfg,
                srcNode: Y.one('#tag_filter'),
                initial_tags: this.get('model').get('tag_str').split(' ')
            });
        },

        _validate_settings: function () {
            var errors = [],
                settings = this.get('settings'),
                required = [
                    'api_url',
                    'api_username',
                    'api_key'
                ];

            Y.Array.each(required, function (key) {
                if (!settings.get(key)) {
                    errors.push("The value for " + key + " has not been set");
                }
            });

            // display errors if we have them
            if (errors.length) {
                return false;
            } else {
                return true;
            }

        },

        events: {
            '#form': {
                submit: '_handle_save'

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
            // validate the settings
            var valid = this._validate_settings();

            if (!valid) {
                var n = new Y.bookie.chrome.Notification({
                    code: '9999',
                    type: 'error',
                    short_text: 'Error',
                    long_text: 'The extension settings are not valid. Please go to the options page and update them.'
                });
            }

            this.api_cfg = this.get('settings').get_apicfg();

            // fire the ajax request to see if the model can be updated
            var m = this.get('model');
            m.set('api_cfg', this.api_cfg);
            m.load({
                hash_id: m.get('hash_id')
            });

            // setup the form with the current model data
            this._init_form();

            // bind to the event that if the model changes, check it for the
            // suggested tags to show/update the form?

            // see if we should be loading the page content
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
             * @default undefined
             * @type Y.bookie.Bmark
             *
             */
            model: {},

            /**
             * We need to know the settings on the extension in order to
             * operate the View and handle storing and fetching the bookmark
             * data.
             *
             * @attribute settings
             * @default undefined
             * @type Object
             *
             */
            settings: {
            }
        }
    });

    // ns.Chrome = Y.Base.create('bookie-chrome-popup', Y.Base, [], {

    //     _init_popup: function () {
    //         // bind up the TagControl to get that UI flash over with asap
    //         var tagcontrol = new Y.bookie.TagControl({
    //            api_cfg: api_cfg,
    //            srcNode: Y.one('#tag_filter'),
    //            initial_tags: tags
    //         });
    //         tagcontrol.render();

    //         // input with the tag plugin version
    //         Y.one('div.yui3-bookie-tagcontrol input').focus();

    //         Y.one('#form').on('submit', this.save, this);
    //         this.init_form_data('chrome-extension');

    //         /**
    //          * Load the data for the current page in case we've got data on it
    //          *
    //          */
    //         var api_cfg = this.settings.getAttrs();
    //         api_cfg.hash_id = hash_url(this.bookmark.url);
    //         var api = new Y.bookie.Api.route.Bmark(API_CFG);

    //         api.call({
    //             success: function (data, request) {

    //             },
    //             error: function (data, status_str, response) {

    //             }
    //         });

    //         // $($b.EVENTID).trigger($b.events.LOAD, current_tab_info);

    //         /**
    //          *
    //          * @todo
    //          * This is all about setting up the suggested tags for use. We
    //          * need to bind click events, etc when used. We'll add that back
    //          * in later
    //          *
    //          */
    //         // $($b.EVENTID).bind($b.events.DUPE_TAGS, $b.ui.dupe_tags);
    //         // $('#latest_tags').delegate('a', 'click', function (ev) {
    //         //     ev.preventDefault();
    //         //     $b.ui.dupe_tags($(this));
    //         // });
    //     },

    //     /**
    //      * We need to fill in a bunch of our form data in order to be able to
    //      * move forward with things
    //      *
    //      * @param inserted_by string for how this is getting saved, the toread
    //      * right click option, the chrome extension itself, etc?
    //      *
    //      */
    //     init_form_data: function (inserted_by) {
    //         Y.one('#url').set('value', this.bookmark.url);
    //         Y.one('#description').set('value', this.bookmark.description);
    //         Y.one('#inserted_by').set('value', inserted_by);
    //         Y.one('#extended').set('value', "");
    //         console.log('populating form base');
    //     },

    //     _setup_readable_content: function () {
    //         // don't worry about loading the content of the page if we
    //         // don't have it set in our options
    //         if(!localStorage['cache_content'] || localStorage['cache_content'] != "true") {
    //             // then skip it, we don't want the added load on the
    //             // browser or the server
    //         } else {
    //             bkg = chrome.extension.getBackgroundPage();

    //             bkg.inject_readable(function () {
    //                 Y.one('#content').set('value', bkg.get_html_content());
    //             });
    //         }

    //     },

    //     initializer: function (cfg) {
    //         this.settings = new ns.Settings();
    //         this.bookmark = new Y.bookie.Bmark(cfg.url_data);

    //         // we can only go on if the settings are ok
    //         if (!this.valid_settings()) {
    //             // the errors are displayed by the error code, yea this should
    //             // be split out I know...but time heals all code wounds
    //             // right?...right?
    //             return;
    //         } else {
    //             // now let's bind up the popup and make it all work
    //             this._init_popup();
    //             this._setup_readable_content();
    //         }
    //     },

    //     valid_settings: function () {
    //         var errors = new ns.PopupErrors();

    //         settings = this.settings;

    //         var required = [
    //             'api_url',
    //             'api_username',
    //             'api_key'
    //         ];

    //         Y.Array.each(required, function (key) {
    //             if (!setting.get(key)) {
    //                 errors.add("The value for " + key + " has not been set");
    //             }
    //         });

    //         // display errors if we have them
    //         if (errors.length) {
    //             errors.render();
    //             return false;
    //         } else {
    //             return true;
    //         }
    //     },
    // }, {
    //     ATTRS: {
    //         /**
    //          * When we init we want to tell the chrome extension about the
    //          * current url. It's passed into via this url data from the chrome
    //          * extension api that has the url and title of the current page
    //          *
    //          */
    //         url_data: {},
    //     }
    // });


    ns.Errors = Y.Base.create('bookie-chrome-errors', Y.Base, [], {
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
            },

            target_node: {
                valueFn: function () {
                    return Y.one('#errors');
                }
            }
        }
    });


    ns.Notification = Y.Base.create('bookie-chrome-notification',
        Y.Base, [], {

            initializer: function (cfg) {
                if (window.chrome !== undefined && chrome.tabs) {
                    if(this.get('type') === "error") {
                        //show a desktop notification
                        var n = webkitNotifications.createNotification(
                            'logo.128.png',
                            this.get('short_text'),
                            this.get('long_text')
                            );
                        n.show();

                        //hide the desktop notification after 5 seconds
                        window.setTimeout(function() {
                            n.cancel();
                        }, 5000);
                    } else {
                        // some post notify checks
                        if (this.get('long_text') === "saved") {
                            chrome.tabs.getSelected(null, function (tab) {
                                // we need to hash this into storage
                                var hash_id = Y.bookie.Hash.hash_url(tab.url);
                                localStorage.setItem(hash_id, 'true');
                            });
                            window.close();
                        }
                    }
                }
            }
        }, {
            ATTRS: {
                code: {},
                type: {},
                short_text: {},
                long_text: {},
            }
        }
    );

    ns.Badge = Y.Base.create('bookie-chrome-badge', Y.Base, [], {
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
                    console.log("Unknown notification type: " +
                                notification.type);
            };

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
    requires: ['base', 'node', 'view', 'bookie-model', 'bookie-tagcontrol', 'bookie-api']
});

