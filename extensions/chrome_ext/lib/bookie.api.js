/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

/**
 * Split out the API calls into a reusable library to try to help reuse among
 * extensions, mobile, and main site
 *
 */
var bookie = (function (opts) {
    var $b = opts.bookie,
        $ = opts.jquery;

    $b.log = opts.console_log.log;
    $b.api = {
        'init': function(app_url, username, api_key) {
            $b.api.opt = {};
            $b.api.opt.app_url = app_url;
            $b.api.opt.username = (username ? username : '');
            $b.api.opt.api_key = (api_key ? api_key : '');
        }
    };


    /**
     * Base request object that our custom ones will extend
     *
     */
    $b.api._request = function (options) {
        var defaults, opts;


        // if we already have an error, move it so we can use it as a callback
        if (options.error) {
            options.error_callback = options.error;
            options.error = undefined;
        }

        defaults = {
            type: "GET",
            dataType: "json",
            data: {},
            context: $b,
            timeout: 30000,
            error: function(jqxhr, textStatus, errorThrown) {
                var data = $.parseJSON(jqxhr.responseText),
                    status_str = textStatus;

                // hand the callback the issue at hand
                options.error_callback(data, status_str);
            }
        };

        // now fill in any %s/etc params
        options.url = $b.api.opt.app_url + options.url;
        options.url = _.sprintf(options.url, $b.api.opt.username);

        opts = $.extend({}, defaults, options);

        if ($b.api.opt.api_key !== undefined) {
            opts.data.api_key = $b.api.opt.api_key;
        }

        $.ajax(opts);
    };


    /**
     * Recent calls the json api for a list of recent bookmarks
     *
     * @param options is a set of paging information, with_content flag
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.recent = function (options, callbacks) {
        // we need to get the list of recent from the api
        var url = "/api/v1/%s/bmarks",
            data = {
                'count': 10,
                'page': 1,
                'with_content': false
            },
            opts = {
                url: url,
                data: $.extend(data, options),
                success: callbacks.success,
                complete: callbacks.complete
            };

        $b.api._request(opts);
    };


    /**
     * Popular bookmarks json api call
     *
     * @param options is an object of the url parameters the api takes
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.popular = function (options, callbacks) {
        // we need to get the list of recent from the api
        var url = "/api/v1/%s/bmarks/popular",
            data = {
                'count': 10,
                'page': 1,
                'with_content': false
            },
            opts = {
                url: url,
                data: $.extend(data, options),
                success: callbacks.success,
                complete: callbacks.complete
            };

        $b.api._request(opts);
    };


    /**
     * Store/Update a bookmark in the system
     *
     * @param data is an object of all the parameters sent to store
     *        url, description, extended, tags, etc
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.add = function (data, callbacks) {
        var url = "/api/v1/%s/bmark",
            opts = {
                type: 'post',
                url: url,
                data: data,
                success: callbacks.success,
                error: callbacks.error
            };
        $b.api._request(opts);
    };


    /**
     * Get a bookmark from the json api
     *
     * @param %s to make the request as
     * @param hash_id is hash from the bookmark url used to find and reference
     *                it
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.bookmark = function (hash_id, options, callbacks) {
        // we need to get the list of recent from the api
        var url = "/api/v1/%s/bmark/" + hash_id,
            data = {
                'get_last': false,
                'with_content': false
            },
            opts = {
                url: url,
                data: $.extend(data, options),
                success: callbacks.success,
                error: callbacks.error
            };

        $b.api._request(opts);
    };


    /**
     * By default a delete will have the data() passed into the POST, so we
     * need to manually override the api_key into the url ourselves
     *
     */
    $b.api.remove = function (hash_id, callbacks) {
        var url = "/api/v1/%s/bmark/" + _.sprintf("%s?api_key=%s",
                                                  hash_id,
                                                  $b.api.opt.api_key),
            opts = {
                url: url,
                type: "delete",
                success: callbacks.success,
                error: callbacks.error
            };

        $b.api._request(opts);
    };


    /**
     * Perform a search via the json api
     *
     * @param terms is an array of search terms
     * @param options do you want to search content, count/page info
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.search = function (terms, options, callbacks) {
        // we need to get the list of recent from the api
        var url_terms = terms.join("/"),
            url = "/api/v1/%s/bmarks/search/" + url_terms,
            data = {
                'search_content': false,
                'count': 10,
                'page': 0
            },
            opts = {
                url: url,
                data: $.extend(data, options),
                success: callbacks.success,
                complete: callbacks.complete
            };

        $b.api._request(opts);
    };


    /**
     * Suggest tag completion options based on the given tag string
     *
     * @param tag the part of a tag we want to complete against
     * @param current an array of current tags already selected to provide
     *                relevence
     * @param callbacks is an object of success, complete, error callbacks
     *
     */
    $b.api.tag_complete = function (options, callbacks) {
        var data = {
                'tag': "",
                'current': ""
            },
            opts = {
                url: "/api/v1/%s/tags/complete",
                data: $.extend(data, options),
                success: callbacks.success,
            };

        $b.api._request(opts);
    };


    /**
     * Get the full list of hashes for the existing urls we have
     * Used to sync the cache of hashes on the extensions
     *
     * @param callbacks is an object of success, complete, error callbacks
     *
     */
    $b.api.sync = function (callbacks) {
        opts = {
            url: "/api/v1/%s/extension/sync",
            success: callbacks.success
        };

        if (callbacks.error !== undefined) {
            opts.error = callbacks.error;
        }

        $b.api._request(opts);

    };


    /**
     * Fetch the api key for the currently logged in user
     *
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.api_key = function (callbacks) {
        // we need to get the list of recent from the api
        var url = "/api/v1/%s/api_key",
            opts = {
                url: url,
                success: callbacks.success
            };

        $b.api._request(opts);
    };


    /**
     * Change the user's password
     *
     * @param option - object of the url parameters pass
     * @param callbacks used with the api call
     *
     */
    $b.api.change_password = function (options, callbacks) {
        var url = "/api/v1/%s/password",
            data = {
                'current_password': "",
                'new_password': ""
            },
            opts = {
                url: url,
                type: 'post',
                data: $.extend(data, options),
                success: callbacks.success,
                error: callbacks.error
            };

        $b.api._request(opts);
    };


    /**
     * Change the user's account details
     *
     * @param data posted new account params
     * @param callbacks used with the api call
     *
     */
    $b.api.account_update = function (new_data, callbacks) {
        var url = "/api/v1/%s/account",
            data = new_data,
            opts = {
                url: url,
                data: data,
                type: "post",
                success: callbacks.success
            };

        $b.api._request(opts);
    };


    /**
     * Mark the user account to go through reactivation procedures
     *
     * @param options post parameters passed to suspend the account
     * @param callbacks used with the api call
     *
     */
    $b.api.reactivate = function (options, callbacks) {
        var url = "/api/v1/suspend",
            data = { 'email': "" },
            opts = {
                url: url,
                type: 'post',
                data: $.extend(data, options),
                success: callbacks.success,
                error: callbacks.error
            };

        $b.api._request(opts);
    };


    /**
     * Activate the account after being deactivated
     *
     * @param options url parameters passed to the api see he api docs
     * @param callbacks
     *
     */
    $b.api.activate = function (options, callbacks) {
        var url = "/api/v1/suspend",
            data = {
                'code': "",
                'username': "",
                'password': ""
            },
            opts = {
                url: url,
                type: 'get',
                data: $.extend(data, options),
                success: callbacks.success,
                error: callbacks.error
            };

        $b.api._request(opts);
    };

    return $b;
})(bookie_opts);
