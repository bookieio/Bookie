/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

/**
 * Split out the Misc util methods we want to share among front ends
 * extensions, mobile, and main site
 *
 */
var bookie = (function (opts) {
    var $b = opts.bookie,
        $ = opts.jquery;

    $b.log = opts.console_log.log;
    $b.utils = {

        // hash the url into our defined mechanism
        'hash_url': function (url) {
            $b.log('Hashing url: ' + url);
            var hash = Sha256.hash(url, true).substr(0, 14);
            return hash;
        },

        // verify that our url is bookmarked or not
        // using the bookie.settings api to check
        'is_bookmarked': function (url) {
            var hash_id = bookie.utils.hash_url(url),
                found = bookie.settings.get(hash_id);

            if (found !== null) {
                return true;
            } else {
                return false;
            }
        }
    };

    return $b;
})(bookie_opts);
