YUI.add('bookie-api', function(Y) {

    // build sprintf onto the Y object?

    Y.namespace('bookie');

    var _ = Y.Lang.substitute;

    /**
     * We want to wrap our ajax calls through the IO module.
     *
     * This will apply the right callback function provided by the caller,
     * allow callers to use default callbacks, and make sure we parse json back
     * to provide to the caller's callback as data
     *
     */
    var request_handler = function (url, cfg, callbacks) {

        // extend with the base handlers for each event we want to use
        // should have cases for complete, success, failure
        // Note: complete fires before both success and failure, not usually
        // the event you want
        var default_complete = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText);

                if (arguments.complete !== undefined) {
                    arguments.complete(data, response);
                } else {

                }
            },
            default_success = function (id, response, arguments) {
                var data = Y.JSON.parse(response.responseText);

                // this is a 200 code and the response text should be json data
                // we need to decode and pass to the callback
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
        cfg.arguments = callbacks;
        cfg.on = {
            complete: default_complete,
            success: default_success,
            failure: default_failure
        };

        var request = Y.io(url, cfg);
    };

    Y.bookie.Api = function() {
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
    }

    Y.extend(Y.bookie.Api, Y.Base, {

        /**
         * Available routes in the API
         *
         */
        routes: {
            'bmarks_all': {
                'url': '/bmarks',
                'data': {
                    'count': 10,
                    'page': 1,
                    'with_content': false
                },
            },
            'bmarks_user': {
                'url': '/{username}/bmarks',
                'data': {
                    'count': 10,
                    'page': 1,
                    'with_content': false
                 }
            },
        },

        base_cfg: {
            method: "GET",
            data: {},
            headers: {
                'Content-Type': 'application/json',
            },
            on: {
                    start: function () {},
                    complete: function () {},
                    end: function () {},
            },
            arguments: {}
        },

        initializer : function(cfg) {
            // first make sure the route we want is valid
            if (!Y.Object.hasKey(this.routes, cfg.route)) {
                throw(_('Selected route is not valid: {route}', cfg));
            }
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

        build_cfg: function () {
            var base_data = this.routes[this.get('route')].data;
            Y.mix(base_data, this.get('options').data);
            this.set('options.data', base_data);
            return this.get('options');
        },

        call: function (callbacks) {
            request_handler(this.build_url(),
                            this.build_cfg(),
                            callbacks);
        }
    });

}, '0.1.0' /* module version */, {
    requires: ['base', 'io', 'querystring-stringify-simple', 'json']
});
