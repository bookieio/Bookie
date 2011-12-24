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

            return this.get('url') + _(this.url, data);
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
            url: '',
            data: {}
        },
        {}
    );


    Y.bookie.Api.route.BmarksAll = Y.Base.create(
        'bookie-api-route-bmarksall',
        Y.bookie.Api.route,
        [], {
            url: '/bmarks',
            data: {
                count: 10,
                page: 1,
                with_content: false
            },

            initializer: function (cfg) {}
        },
        {}
    );


    Y.bookie.Api.route.TagComplete = Y.Base.create(
        'bookie-api-route-tagcomplete',
        Y.bookie.Api.route,
        [], {
            url: '/{username}/tags/complete',
            call: function (callbacks, tag_stub, current_tags) {
                this.set('options', {
                    data: {
                        tag: tag_stub,
                        current: current_tags
                    }
                });
                Y.bookie.Api.route.TagComplete.superclass.call.apply(this, arguments);
            }
        },
        {}
    );


    Y.bookie.Api.route.UserBmarksAll = Y.Base.create(
        'bookie-api-route-user-bmarksall',
        Y.bookie.Api.route,
        [], {
            url: '/{username}/bmarks',
            data: {
                count: 10,
                page: 1,
                with_content: false
            },

            initializer: function (cfg) {}
        },
        {}
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
            url: '/{username}/bmark/{hash_id}',
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
                username: {
                    required: true
                }
            }
        }
    );

        //     bookmark_user: {
        //         url: '/{username}/bmark/{hash_id}',
        //         data: {}
        //     },

        //     bookmark_remove: {
        //         method: "DELETE",
        //         url: '/{username}/bmark/{hash_id}/',
        //         data: {}
        //     },

}, '0.1.0', {
    requires: ['base', 'io', 'querystring-stringify-simple', 'json']
});
