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
     * pager object for api calls.
     * Most api calls accept a page=X&count=Y
     *
     * Pass to api call function as the first parameter. If you want to use
     * defaults you can just pass bookie.api.pager()
     *
     */
    $b.api.pager = function(page, count) {
        var that = {};

        that.page = typeof(page) !== 'undefined' ? page : 0;
        that.count = typeof(count) !== 'undefined' ? count : undefined;

        that.generate_url = function () {
            var url_str = ["page=" + that.page];

            if (that.count !== undefined) {
                url_str.push('count=' + that.count);
            }

            return url_str.join('&');
        };

        return that;
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
     * @param pager is an api.pager object with a page, count parameter
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.recent = function (pager, callbacks) {
        // we need to get the list of recent from the api
        var url = "/api/v1/bmarks/%s/recent?" + pager.generate_url(),
            opts = {
                url: url,
                success: callbacks.success,
                complete: callbacks.complete
            };

        $b.api._request(opts);
    };


    /**
     * Popular bookmarks json api call
     *
     * @param pager is an api.pager object with a page, count parameter
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.popular = function (pager, callbacks) {
        // we need to get the list of recent from the api
        var url = "/api/v1/bmarks/%s/popular?" + pager.generate_url(),
            opts = {
                url: url,
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
    $b.api.bookmark = function (hash_id, callbacks, get_last) {
        // we need to get the list of recent from the api
        var url = "/api/v1/%s/bmark/" + hash_id,
            opts = {
                url: url,
                success: callbacks.success,
                error: callbacks.error
            };

        if (get_last !== undefined) {
            opts.data = {'last_bmark': true};
        }

        $b.api._request(opts);
    };


    $b.api.remove = function (hash_id, callbacks) {
        var url = "/api/v1/%s/bmark/" + hash_id,
            opts = {
                url: url,
                type: "delete",
                success: callbacks.success
            };

        $b.api._request(opts);
    };

    /**
     * Perform a search via the json api
     *
     * @param terms is an array of search terms
     * @param with_content is a flag if we want to search fulltext content
     * @param pager is a pager instances with the page/count params
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.search = function (terms, with_content, pager, callbacks) {
        // we need to get the list of recent from the api
        var url_terms = terms.join("/"),
            build_url = function (terms, pager, with_content) {
                var base = "/api/v1/%s/bmarks/search/",
                    terms_addon = terms.join("/"),
                    pager_addon = pager.generate_url();

                base = base + terms_addon + "?" + pager_addon;
                if (with_content !== undefined) {
                    base = base + "&content=true";
                }

                return base;
            },
            url = build_url(terms, pager, with_content),
            opts = {
                url: url,
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
    $b.api.tag_complete = function (tag, current, callbacks) {
        var opts, req_data = {'tag': tag};

        if (current !== undefined) {
            req_data.current = current.join(" ");
        }

        opts = {
            url: "/api/v1/%s/tags/complete",
            data: req_data,
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
     * @param current password
     * @param new password
     * @param callbacks used with the api call
     *
     */
    $b.api.change_password = function (current_pass, new_pass, callbacks) {
        var url = "/api/v1/%s/password",
            data = {'current_password': current_pass,
                    'new_password': new_pass
            },
            opts = {
                url: url,
                type: 'post',
                data: data,
                success: callbacks.success
            };

        $b.api._request(opts);
    };


    /**
     * Change the user's account details
     *
     * @param data
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
     * @param email of the user we want to reactivate (reset password)
     * @param callbacks used with the api call
     *
     */
    $b.api.reactivate = function (email, callbacks) {
        var url = "/api/v1/suspend",
            data = { 'email': email },
            opts = {
                url: url,
                type: 'post',
                data: data,
                success: callbacks.success
            };

        $b.api._request(opts);
    };

    /**
     * Activate the account after being deactivated
     *
     * @param uesrname
     * @param code
     * @param new_password
     *
     */
    $b.api.activate = function (username, code, new_password, callbacks) {
        var url = _.sprintf("/api/v1/suspend?code=%s&username=%s&password=%s",
                            escape(code),
                            escape(username),
                            escape(new_password)),
            opts = {
                url: url,
                type: 'delete',
                success: callbacks.success
            };

        $b.api._request(opts);
    };

    return $b;
})(bookie_opts);
