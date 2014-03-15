YUI().add('bookie-chrome', function (Y) {
    var ns = Y.namespace('bookie.chrome');

    /**
     * The View object to the extension popup page.
     *
     * @class Popup
     * @extends Y.View
     * @namespace bookie.chrome
     *
     */
    ns.Popup = Y.Base.create('bookie-chrome-view', Y.View, [], {
        /**
         * By default we haven't loaded any recent tags. If we do, update this
         * so that we don't load them again.
         *
         */
        loaded_recent: false,

        /**
         * We need to bind the bookie icon to the site that your settings say
         * you're using. This is because Bookie can be self hosted and it's
         * the only way to know where to link to.
         *
         * @method _bind_site_link
         *
         */
        _bind_site_link: function () {
            var url = this.api_cfg.url;
            url = url.replace(/api\/v1\/?/, '');
            url = url + this.api_cfg.username;
            Y.one('#bookie_site').set('href', url);
        },

        _build_suggested_tags: function (suggestions) {
            // see if we have the last set of tags to add
            var tag_html = new Y.NodeList();
                tag_container = Y.one('#latest_tags');

            for (tag in suggestions) {
                 tag_html.push(Y.Node.create('<a href="" class="prev_tag">' + suggestions[tag] + '</a>'));
            }

            tag_container.appendChild(tag_html);
            Y.one('#suggested_tags').show();
        },

        /**
         * Process deleting a bookmark requested by the extension.
         *
         * @method _handle_delete
         * @param {Event} e
         *
         */
        _handle_delete: function (e) {
            e.preventDefault();

            var model = this.get('model');
            var hashid = model.get('hash_id');

            model.remove(function () {
                localStorage.removeItem(hashid);
                window.close();
            });
        },

        /**
         * Process storing a bookmark via the API.
         *
         * @method _handle_submit
         * @param {Event} e
         *
         */
        _handle_save: function (e) {
            e.preventDefault();
            this.indicator.show();
            var model = this.get('model');

            // we need to make sure the tag control is up to date so that we
            // don't miss any tags. If the user starts typing a tag, and then
            // stops and clicks save, the tag control will not have added the
            // phrase entered as a tag and it gets lost.
            Y.fire('tag:update', {
                type: 'blur',
                target: ''
            });

            // we need to set the content to be part of the model for this
            // request so we can pass it along, even though the content
            // isn't really valid for it.
            model.addAttr('content', {});

            // we have to do these changes in one fell swoop to prevent a mass
            // firing of the "init_model" callback on the model:change event
            model.setAttrs({
                url: Y.one('#url').get('value'),
                inserted_by: Y.one('#inserted_by').get('value'),
                description: Y.one('#description').get('value'),
                tags: Y.Array.map(this.tag_control.get('tags'), function (t) {
                    return t.get('text');
                }),
                extended: Y.one('#extended').get('value'),
                content: Y.one('textarea#content').get('value')
            });

            // should just be able to fire the save method on the model and
            // display to the user we're working on it.
            model.save(function (data, request) {
                // make sure that we store that this is a saved bookmark in
                // the localStorage index
                if (data.bmark.hash_id) {
                    localStorage.setItem(data.bmark.hash_id, 'true');
                }

                // update the badge now that we've saved
                var b = new Y.bookie.chrome.Badge();
                b.success();
                window.close();
            });
        },

        /**
         * When a user clicks on a suggested tag, get it into our tag control
         * and clear it from the suggested tags.
         *
         * @method _handle_suggested_tag
         * @param {Event} ev
         * @private
         *
         */
        _handle_suggested_tag: function (ev) {
            ev.preventDefault();
            var target = ev.currentTarget;
            Y.fire('tag:add', {
                tag: target.get('text')
            });
            target.remove();
        },

        /**
         * Bind the model up with the form and display it's values into the
         * fields.
         *
         * @method _init_form
         *
         */
        _init_form: function () {
            var model = this.get('model');
            // update the fields with model data
            Y.one('#url').set('value', model.get('url'));
            Y.one('#description').set('value', model.get('description'));
            Y.one('#tag_filter').set('value', model.get('tag_str'));
            Y.one('#extended').set('value', model.get('extended'));
            Y.one('#inserted_by').set('value', 'chrome_ext');

            // make the tag field a TagControl, but only if it's not already one.
            // Once this is done, we need to make sure we update the tags from
            // the model correctly since we need to talk to the TagControl
            // now, and not the tag_filter input element.
            if (!Y.one('.yui3-bookie-tagcontrol')) {
                this.tag_control = new Y.bookie.TagControl({
                    api_cfg: this.api_cfg,
                    srcNode: Y.one('#tag_filter'),
                    initial_tags: model.get('tag_str').split(' '),
                    with_submit: false
                });
                this.tag_control.render();
            } else {
                // update the tags via the TagControl
                var tags = model.get('tags');
                Y.Array.each(tags, function (t) {
                    this.tag_control.add(t.name);
                }, this);
            }

            this._bind_site_link();

            // if we've gotten back a last bookmark, then make sure we build a
            // list of tags for the clicking in the view
            if (!this.loaded_recent && model.get('last')) {
                // find any tags and pass them to the suggestion handler
                this.loaded_recent = true;
                var tag_str = model.get('last').tag_str;
                if (tag_str.length) {
                    this._build_suggested_tags(tag_str.split(' '));
                }
            }

            if (model.get('bid')) {
                var delete_button = Y.one('#delete');
                delete_button.show();
            }
        },

        _validate_settings: function () {
            var errors = [],
                ret,
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

            // Verify the auth credentials are not the default values.
            var defaults = new Y.bookie.OptionsModel();
            if (settings.get('api_username') === defaults.get('api_username')) {
                errors.push("The api username must be set.");
            }

            if (settings.get('api_key') === defaults.get('api_key')) {
                errors.push("The api key must be set.");
            }

            // display errors if we have them
            if (errors.length) {
                ret = false;
            } else {
                ret = true;
            }

            return ret;
        },

        events: {
            '#form': {
                submit: '_handle_save'
            },
            '#delete': {
                'click': '_handle_delete'
            },
            '#bookie_site': {
                'click': '_bookie_instance_link'
            },
            '.prev_tag': {
                'click': '_handle_suggested_tag'
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
                    title: 'Error',
                    message: 'The extension settings are not valid. Please go to the options page and update them.'
                });

                var b = new Y.bookie.chrome.Badge();
                b.show_error();

                return;
            }

            this.api_cfg = this.get('settings').get_apicfg();
            this.indicator = new Y.bookie.Indicator({
                target: Y.one('#form_overlay')
            });
            this.indicator.render();

            // bind to the event that if the model changes, check it for the
            // suggested tags to show/update the form?
            this.get('model').on('change', this._init_form, this);

            // fire the ajax request to see if the model can be updated
            var m = this.get('model');
            m.load({
                hash_id: m.get('hash_id')
            });

            // setup the form with the current model data
            this._init_form();
        },

        render: function () {
            // We need to make sure we hit the container so that our events
            // are bound to our container since it's not lazy loaded via YUI.
            this.get('container');
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


    /**
     * Display Chrome notification windows to the user.
     *
     * @class Notification
     * @extends Y.Base
     * @namespace bookie.chrome
     *
     */
    ns.Notification = Y.Base.create('bookie-chrome-notification',
        Y.Base, [], {

            /**
             * The notification init shows and runs the whole thing.
             *
             * @method initializer
             * @param {Object} cfg
             *
             */
            initializer: function (cfg) {
                if (window.chrome !== undefined && chrome.tabs) {
                    if(this.get('type') === "error") {
                        //show a desktop notification
                        var n = webkitNotifications.createNotification(
                            'logo.128.png',
                            this.get('title'),
                            this.get('message')
                            );
                        n.show();

                        //hide the desktop notification after 5 seconds
                        window.setTimeout(function() {
                            n.cancel();
                        }, 5000);
                    } else {
                        // some post notify checks
                        if (this.get('description') === "saved") {
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
                /**
                 * Valid values are info and error at the moment.
                 *
                 * @attribute type
                 * @default info
                 * @type String
                 *
                 */
                type: {
                    value: 'info'
                },

                /**
                 * @attribute title
                 * @default ''
                 * @type String
                 *
                 */
                title: {
                    value: ''
                },

                /**
                 * @attribute message
                 * @default ''
                 * @type String
                 *
                 */
                message: {
                    value: ''
                },
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

        clear: function (ms) {
            var ttl = ms || 0;
            window.setTimeout(function() {
                chrome.browserAction.setBadgeText({text: ''});
            }, ttl);
        },

        _set_badge: function (text, bgcolor, hidetime) {
            if (bgcolor) {
                chrome.browserAction.setBadgeBackgroundColor({color: bgcolor});
            }

            chrome.browserAction.setBadgeText({text: text});

            if (hidetime) {
                this.clear(hidetime);
            }
        },

        initializer: function () {},

        /**
         * Update the badge to reprsent that the url is bookmarked.
         *
         * @method is_bookmarked
         *
         */
        is_bookmarked: function () {
            this._set_badge('+', this._colors.blue);
        },

        show_error: function () {
            this._set_badge('Err', this._colors.red, this.get('time'));
        },

        success: function () {
            this._set_badge('Ok', this._colors.green, this.get('time'));
        },

        removed: function () {
            this._set_badge('Del', this._colors.green, this.get('time'));
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


    ns.BackgroundPage = Y.Base.create('bookie-chrome-background', Y.Base, [], {
        _check_url_bookmarked: function (url) {
            var is_bookmarked =
                localStorage.getItem(Y.bookie.Hash.hash_url(url));

            // check if we have this bookmarked
            // if so update the badge text with +
            if (is_bookmarked === 'true') {
                this.badge.is_bookmarked();
            } else {
                this.badge.clear();
            }
        },

        initializer: function (cfg) {
            this.badge = new Y.bookie.chrome.Badge();
            this.settings = new Y.bookie.OptionsModel();
            this.settings.load();
        },

        init_background: function () {
            var that = this;

            // Keep checking until the user configures a working
            // combination for the first time.
            chrome.storage.local.get("optionsConfigured", function(obj) {
                if (!obj["optionsConfigured"]) {
                    chrome.tabs.create({
                        url: "options.html"
                    });
                    var n = new Y.bookie.chrome.Notification({
                        code: '9999',
                        type: 'error',
                        title: 'Options Not Configured',
                        message: 'To start using the extension, fill in the api_key, api_username and the api_url'
                    });
                }
            });

            // bind to the events to check if the current url is bookmarked or not
            chrome.tabs.onUpdated.addListener(
                function(tabId, changeInfo, tab) {
                    var tid = tabId;
                    console.log('on updated');

                    // we only want to grab this if we change the current url in
                    // the current tab
                    if ('url' in changeInfo) {
                        if (tab.url) {
                            chrome.tabs.getSelected(undefined, function (tab) {
                                if (tid === tab.id) {
                                    that._check_url_bookmarked(tab.url);
                                }
                            });
                        } else {
                            console.log('no hash for you');
                        }
                    }
                }
            );

            chrome.tabs.onSelectionChanged.addListener(
                function(tabId, changeInfo) {
                    chrome.tabs.get(tabId, function (tab) {
                        if (tab.url) {
                            that._check_url_bookmarked(tab.url);
                        } else {
                            console.log('no hash for you');
                        }
                    });
                }
            );

            // chrome.contextMenus.create({
            //     "title": "Read Later",
            //     "contexts":["page"],
            //     "onclick": this.read_later
            // });

            /**
             * This addListener is for the shortcut.js. It means that we want
             * to open the extension with this url.
             *
             */
            chrome.extension.onRequest.addListener(
                function(request, sender, sendResponse) {
                    if (request.url) {
                        chrome.tabs.getSelected(null, function(tab_obj) {
                            var encoded_url = window.btoa(tab_obj.url),
                                encoded_title = window.btoa(tab_obj.title),
                                hash = [encoded_url, encoded_title].join('|');

                            chrome.tabs.create({url: "popup.html#" + hash});
                        });
                    }
                }
            );
        }
    }, {
        ATTRS: {

        }
    });

}, '0.1', {
    requires: ['base', 'node', 'view', 'bookie-model', 'bookie-tagcontrol', 'bookie-api', 'bookie-indicator']
});

