/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */

/**
 * Javascript implementation of the Bookie API used on the app front end and
 * sample implementation itself.
 *
 */

YUI.add('bookie-api', function (Y) {

    Y.namespace('bookie');

    var _ = Y.Lang.substitute;

    /**
     * We want to wrap our ajax calls through the IO module.
     *
     * This will apply the right callback function provided by the caller,
     * allow callers to use default callbacks, and make sure we parse json
     * back to provide to the caller's callback as data
     *
     */
    var request_handler = function (url, cfg, arguments) {
        // extend with the base handlers for each event we want to use
        // should have cases for complete, success, failure
        // Note: complete fires before both success and failure, not usually
        // the event you want
        var request,
            default_complete = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText);

                if (arguments.callbacks.complete !== undefined) {
                    arguments.callbacks.complete(data, response, arguments);
                } else {

                }
            },
            default_success = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText);

                // this is a 200 code and the response text should be json
                // data we need to decode and pass to the callback
                if (arguments.callbacks.success !== undefined) {
                    arguments.callbacks.success(data, response, arguments);
                } else {

                }
            },
            default_failure = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText),
                    status_str = response.statusText;

                // hand the callback the issue at hand
                if (arguments.callbacks.error !== undefined) {
                    arguments.callbacks.error(
                        data,
                        status_str,
                        response,
                        arguments);
                } else {

                }
            };

        // bind the callbacks the caller sent us to be used as the callbacks
        // but keep any other arguments we've already assigned
        cfg.on = {
            complete: default_complete,
            success: default_success,
            failure: default_failure
        };

        // if the request is a POST request, then we need to JSON the data
        // body
        if (cfg.method == "POST") {
            cfg.data = Y.JSON.stringify(cfg.data);
        }

        cfg.arguments = arguments;
        request = Y.io(url, cfg);
    };

    Y.bookie.Api = Y.Base.create('bookie-api', Y.Base, [], {
        base_cfg: {
            method: "GET",
            data: {},
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            on: {
                start: function () {},
                complete: function () {},
                end: function () {},
            },
            arguments: {}
        },

        initializer : function (cfg) {},

        /**
         * Generate a full api url to call
         *
         * If user_username is true then perform a replace on the given url
         * with the api instance's username parameter
         *
         */
        build_url: function (data) {
            // make sure the username is in the config as well
            if (Y.Lang.isObject(data)) {
                data.username = this.get('username');
            } else {
                data = {
                    username: this.get('username')
                }
            }
            return this.get('url') +
                Y.Lang.substitute(this.get('url_element'), data);
        },

        /**
         * The cfg passed to the IO module needs to be combined with the
         * default data set and then any options passed in from the caller
         *
         * Order is passed in options -> base_cfg
         *
         */
        build_cfg: function () {
            // first build the base config with the routes config
            // this updates things like GET vs POST and such
            var call_cfg = this.get('options'),
                base_cfg = this.base_cfg,
                base_data = this.data;

            // mix them over each other, not sure this works for nested bits
            // though, for instance base_cfg might have cfg.data.query_param
            // that needs to be kept as we overlay it with the other settings
            // same with the callbacks and such
            base_cfg = Y.merge(base_cfg, call_cfg);

            // next update with the routes info and other hard coded request
            // data
            base_cfg.data = Y.merge(base_cfg.data, base_data, call_cfg.data);

            // if we have an api key, then we need to pass that along as well
            if (this.get('api_key').length > 2) {
                if (base_cfg.data) {
                    base_cfg.data.api_key = this.get('api_key');
                } else {
                    base_cfg.data = {
                        api_key: this.get('api_key')
                    }
                }
            }

            return base_cfg;
        },

        /**
         * Actually make the ajax call with the given cfg we've setup for use.
         *
         * @param callbacks an object of success/error/complete callbacks
         * we'll hand json decoded data of the response
         *
         */
        call: function (callbacks) {
            // make sure we stick the callbacks on arguments in the base cfg
            // before we build the rest of it
            var args = this.base_cfg.arguments,
                cfg = this.build_cfg();

            args.callbacks = callbacks;

            request_handler(this.build_url(cfg.data),
                            cfg,
                            args);
        }
    }, {
           ATTRS: {
               api_key: {
                   value: ""
               },

               options: {
                   value: {}
               },

               url: {
                   value: "",
                   writeOnce: true
               },

               username: {
                   value: ""
               }
            }
        }
    );


    Y.bookie.Api.route = Y.Base.create(
        'bookie-api-route',
        Y.bookie.Api,
        [],
        {
            data: {}
        },
        {
            ATTRS: {
                url_element: {
                    value: ''
                }
            }
        }
    );


    Y.bookie.Api.route.BmarksAll = Y.Base.create(
        'bookie-api-route-bmarksall',
        Y.bookie.Api.route,
        [], {
            data: {
                count: 10,
                page: 1,
                with_content: false
            },

            initializer: function (cfg) {
            }
        }, {
            ATTRS: {
                /**
                 * Any tags to filter on
                 *
                 */
                tags: {
                    valueFn: function () {
                        return [];
                    }
                },

                url_element: {
                    value: '/bmarks',
                    getter: function () {
                        if (this.get('tags')) {
                            return [
                                '/bmarks',
                                this.get('tags').join('/')
                            ].join('/');
                        } else {
                            return '/bmarks';
                        }

                    }
                }
            }
        }
    );


    Y.bookie.Api.route.TagComplete = Y.Base.create(
        'bookie-api-route-tagcomplete',
        Y.bookie.Api.route,
        [], {
            call: function (callbacks, tag_stub, current_tags) {
                this.set('options', {
                    data: {
                        tag: tag_stub,
                        current: current_tags
                    }
                });
                Y.bookie.Api.route.TagComplete.superclass.call.apply(this, arguments);
            }
        }, {
            ATTRS: {
                url_element: {
                    value: '/{username}/tags/complete'
                }
            }
        }

    );


    Y.bookie.Api.route.UserBmarksAll = Y.Base.create(
        'bookie-api-route-user-bmarksall',
        Y.bookie.Api.route,
        [], {
            data: {
                count: 10,
                page: 1,
                with_content: false
            },

            initializer: function (cfg) {}
        }, {
            ATTRS: {
                url_element: {
                    value: '/{username}/bmarks'
                }
            }
        }
    );


    /**
     * API call to fetch a bookmark object.
     *
     * Since it must have been bookmarked by someone, and the hash belongs to
     * them, you need the user and the hash_id of the bookmark to load it.
     *
     * This is NOT the username of a logged in/api user. It's the username of
     * the person that bookmarked the url.
     *
     */
    Y.bookie.Api.route.Bmark = Y.Base.create(
        'bookie-api-route-bmark',
        Y.bookie.Api.route,
        [], {
            initializer: function (cfg) {
                this.data = {
                    hash_id: this.get('hash_id'),
                    username: this.get('username')
                }
            }
        }, {
            ATTRS: {
                hash_id: {
                    required: true
                },
                url_element: {
                    value: '/{username}/bmark/{hash_id}'
                },
                username: {
                    required: true
                }
            }
        }
    );


    Y.bookie.Api.route.UserBmarkDelete = Y.Base.create(
        'bookie-api-route-user-bmark-delete',
        Y.bookie.Api.route,
        [], {
            initializer: function (cfg) {
                // force this to a DELETE request by overriding our base_cfg
                // we extend.
                this.base_cfg.method = 'DELETE',

                // we have to have a hash_id for our url to be built from
                this.data = {
                    hash_id: this.get('hash_id'),
                }
            }
        }, {
            ATTRS: {
                url_element: {
                    value: '/{username}/bmark/{hash_id}'
                },
                hash_id: {
                    required: true
                }
            }
        }
    );


    Y.bookie.Api.route.UserApiKey = Y.Base.create(
        'bookie-api-route-user-api-key',
        Y.bookie.Api.route,
        [], {
            initializer: function (cfg) {
            }
        }, {
            ATTRS: {
                url_element: {
                    value: '/{username}/api_key'
                }
            }
        }
    );

    Y.bookie.Api.route.UserPasswordChange = Y.Base.create(
        'bookie-api-route-user-password-change',
        Y.bookie.Api.route,
        [], {
            initializer: function (cfg) {
                this.base_cfg.method = 'POST',

                // we have to have current_password, new_password
                this.data = {
                    current_password: this.get('current_password'),
                    new_password: this.get('new_password')
                }
            }
        }, {
            ATTRS: {
                current_password: {
                    required: true
                },
                new_password: {
                    required: true
                },
                url_element: {
                    value: '/{username}/password'
                }
            }
        }
    );


    Y.bookie.Api.route.UserAccountChange = Y.Base.create(
        'bookie-api-route-user-account-change',
        Y.bookie.Api.route,
        [], {
            initializer: function (cfg) {
                this.base_cfg.method = 'POST';

                // we have to have current_password, new_password
                var name = this.get('name'),
                    email = this.get('email');

                this.data = {};

                if (name) {
                    this.data.name = name;
                }

                if (email) {
                    this.data.email = email;
                }
            }
        }, {
            ATTRS: {
                name: {},
                email: {},
                url_element: {
                    value: '/{username}/account'
                }
            }
        }
    );

    Y.bookie.Api.route.SuspendUser = Y.Base.create(
        'bookie-api-route-suspend-user',
        Y.bookie.Api.route,
        [], {
            initializer: function (cfg) {
                this.base_cfg.method = 'POST';

                // we have to have current_password, new_password
                this.data = {
                    email: this.get('email')
                }
            }
        }, {
            ATTRS: {
                email: {
                    required: true
                },
                url_element: {
                    value: '/suspend'
                }
            }
        }
    );


    Y.bookie.Api.route.UnSuspendUser = Y.Base.create(
        'bookie-api-route-unsuspend-user',
        Y.bookie.Api.route,
        [], {
            initializer: function (cfg) {
                this.base_cfg.method = 'DELETE';

                // we have to have current_password, new_password
                this.data = {
                    username: this.get('username'),
                    code: this.get('code'),
                    password: this.get('password')
                }
            }
        }, {
            ATTRS: {
                username: {
                    required: true
                },
                code: {
                    required: true
                },
                password: {
                    required: true
                },
                url_element: {
                    value: '/suspend'
                }
            }
        }
    );

}, '0.1.0', {
    requires: ['base', 'io', 'querystring-stringify-simple', 'json']
});
