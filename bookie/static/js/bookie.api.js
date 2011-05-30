/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

/**
 * Split out the API calls into a reusable library to try to help reuse among
 * extensions, mobile, and main site
 *
 */
var bookie = (function ($b, $) {

    $b.api = {};


    $b.api.init = function(app_url) {
        $b.api.app_url = app_url;
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
                console.log('REQUEST_ERROR');
                console.log('Response Code: ' + jqxhr.status);
                console.log('Response Status: ' + textStatus);
                console.log(jqxhr);
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


    return $b;

})(bookie || {}, jQuery);
