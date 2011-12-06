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
    var request_handler = function (url, cfg, callbacks) {

        // extend with the base handlers for each event we want to use
        // should have cases for complete, success, failure
        // Note: complete fires before both success and failure, not usually
        // the event you want
        var request,
            default_complete = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText);

                if (arguments.complete !== undefined) {
                    arguments.complete(data, response);
                } else {

                }
            },
            default_success = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText);

                // this is a 200 code and the response text should be json
                // data we need to decode and pass to the callback
                if (arguments.success !== undefined) {
                    arguments.success(data, response);
                } else {

                }
            },
            default_failure = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText),
                    status_str = response.statusText;

                // hand the callback the issue at hand
                if (arguments.error !== undefined) {
                    arguments.error_callback(data, status_str, response);
                } else {

                }
            };

        // bind the callbacks the caller sent us to be used as the callbacks
        // but keep any other arguments we've already assigned
        cfg.arguments = callbacks;
        cfg.on = {
            complete: default_complete,
            success: default_success,
            failure: default_failure
        };

        request = Y.io(url, cfg);
    };

    Y.bookie.Api = function () {
        // Invoke Base constructor, passing through arguments
        Y.bookie.Api.superclass.constructor.apply(this, arguments);
    };

    Y.bookie.Api.NAME = 'bookie-api';
    Y.bookie.Api.ATTRS = {
        api_key: {
            value: ""
        },

        options: {
            value: {}
        },

        route: {
            value: "",

            // the route must exist to be set
            validator: function (route) {
                return Y.Object.hasKey(this.routes, route);
            }
        },

        url: {
            value: "",
            writeOnce: true
        },

        username: {
            value: ""
        }
    };

    Y.extend(Y.bookie.Api, Y.Base, {

        /**
         * Available routes in the API
         *
         */
        routes: {
            bmarks_all: {
                url: '/bmarks',
                data: {
                    count: 10,
                    page: 1,
                    with_content: false
                },
            },

            bmarks_user: {
                url: '/{username}/bmarks',
                data: {
                    count: 10,
                    page: 1,
                    with_content: false
                }
            },

            bookmark: {
                url: '/bmark/{hash_id}',
                data: {}
            },

            bookmark_user: {
                url: '/{username}/bmark/{hash_id}',
                data: {}
            },

            bookmark_remove: {
                method: "DELETE",
                url: '/{username}/bmark/{hash_id}/',
                data: {}
            },

            tag_complete: {
                url: '/{username}/tags/complete',
                data: {
                    tag: "",
                    current: ""
                }
            }
        },

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

        initializer : function (cfg) {
            // first make sure the route we want is valid
            if (!Y.Object.hasKey(this.routes, cfg.route)) {
                throw (_('Selected route is not valid: {route}', cfg));
            }

            Y.mix(this.base_cfg, cfg);
        },

        /**
         * Generate a full api url to call
         *
         * If user_username is true then perform a replace on the given url
         * with the api instance's username parameter
         *
         */
        build_url: function () {
            return this.get('url') + _(this.routes[this.get('route')].url,
                                       {'username': this.get('username')});
        },

        /**
         * The cfg passed to the IO module needs to be combined with the
         * default data set and then any options passed in from the caller
         *
         * Order is passed in options -> routes defaults -> base_cfg
         *
         */
        build_cfg: function () {
            // first build the base config with the routes config
            // this updates things like GET vs POST and such
            var call_cfg = this.get('options'),
                route = this.get('route'),
                base_cfg = this.base_cfg,
                route_cfg = this.routes[route],
                base_data = this.routes[this.get('route')].data;

            // mix them over each other, not sure this works for nested bits
            // though, for instance base_cfg might have cfg.data.query_param
            // that needs to be kept as we overlay it with the other settings
            // same with the callbacks and such
            Y.mix(base_cfg, route_cfg, call_cfg);

            // next update with the routes info and other hard coded request
            // data
            Y.mix(call_cfg.data, base_data);
            base_cfg.data = call_cfg.data;

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
            request_handler(this.build_url(),
                            this.build_cfg(),
                            callbacks);
        }
    });

}, '0.1.0', {
    requires: ['base', 'io', 'querystring-stringify-simple', 'json']
});
