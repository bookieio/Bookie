YUI.add('bookie-api', function(Y) {

    Y.namespace('bookie');

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
        url: {
            value: ""
        },

        username: {
            value: ""
        },

        api_key: {
            value: ""
        }
    }

    Y.extend(Y.bookie.Api, Y.Base, {
        base_cfg: {
            method: "GET",
            data: '',
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

        build_url: function (add) {
            return this.get('url') + add;
        },

        build_cfg: function (options) {
            return Y.mix(this.base_cfg, options, true);
        },

        recent: function (options, callbacks) {
            var api_url = '/api/v1/bmarks',
                data = {
                'count': 10,
                'page': 1,
                'with_content': false
            };

            // combine/overwrite data with anything the caller passes in
            Y.mix(data, options.data, true);
            options.data = data;

            request_handler(this.build_url(api_url),
                            this.build_cfg(options),
                            callbacks);
        }
    });


}, '0.1.0' /* module version */, {
    requires: ['base', 'io', 'json']
});
