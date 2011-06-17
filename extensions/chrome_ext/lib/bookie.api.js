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
        'init': function(app_url) {
            $b.api.app_url = app_url;
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

        defaults = {
            type: "GET",
            dataType: "json",
            context: $b,
            timeout: 30000,
            error: function(jqxhr, textStatus, errorThrown) {
                $b.log('REQUEST_ERROR');
                $b.log('Response Code: ' + jqxhr.status);
                $b.log('Response Status: ' + textStatus);
                $b.log(jqxhr);
            }
        };

        options.url = $b.api.app_url + options.url;

        opts = $.extend({}, defaults, options);
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
        var url = "/api/v1/bmarks/recent?" + pager.generate_url(),
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
        var url = "/api/v1/bmarks/popular?" + pager.generate_url(),
            opts = {
                url: url,
                success: callbacks.success,
                complete: callbacks.complete
            };

        $b.api._request(opts);
    };


    /**
     * Get a bookmark from the json api
     *
     * @param hash_id is hash from the bookmark url used to find and reference
     *                it
     * @param callbacks is an object of success, complete, error
     *
     */
    $b.api.bookmark = function (hash_id, callbacks) {
        // we need to get the list of recent from the api
        var url = "/api/v1/bmarks/" + hash_id;
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
        var url = "/api/v1/bmarks/add",
            opts = {
                type: 'post',
                url: url,
                data: data,
                success: callbacks.success
            };
        $b.api._request(opts);
    };


    $b.api.remove = function (bmark_url, api_key, callbacks) {
        var url = "/api/v1/bmarks/remove",
            opts = {
                url: url,
                type: "post",
                data: {
                        'url': bmark_url,
                        'api_key': api_key
                },
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
                var base = "/api/v1/bmarks/search/",
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
            url: "/api/v1/tags/complete",
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
    $b.api.sync = function (api_key, callbacks) {
        opts = {
            url: "/api/v1/bmarks/sync",
            data: {
                    'api_key': api_key
            },
            success: callbacks.success
        };

        $b.api._request(opts);

    };

    return $b;

})(bookie_opts);
