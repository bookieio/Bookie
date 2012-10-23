/**
 * Keep up RSS feed link properties.
 *
 * RSS link needs to be kept up to date based on changes to the client side
 * view. If a user filters on a tag, they'll want the rss feed to include that
 * tag so that the feed matches what they're seeing in the list.
 *
 * @namespace bookie
 * @module rsswatch
 *
 */
YUI.add('bookie-rsswatch', function (Y) {
    var ns = Y.namespace('bookie.rsswatch');

    /**
     * Helper function to bind up a single watcher to the page.
     *
     * @method bookie.rsswatch.watch
     *
     */
    ns.watch = function () {
        var watcher = ns.Updater();
        watcher.bind();
    };

    /**
     * Helper that watches over all powerful things to update RSS.
     *
     * @class RSSWatch.Updater
     * @extends  Y.base
     *
     */
    ns.Updater = Y.Base.create('bookie-rsswatch-updater', Y.Base, [], {
        /**
         * Bind all events to monitor for changes effecting rss url.
         *
         * @method _bind_events
         * @private
         *
         */
        _bind_events: function () {
            // Potential changes are tags and pagination

            // We need to watch for a new event that the api should shout
            // about what url was just loaded so that we can s/recent/rss it
            // and update the rss feed.


            // We need this for both the BmarksAll and UserBmarksAll

        },

        /**
         * Given the data url generated, update it to the valid rss url.
         *
         * @method _generate_updated_url
         * @param {String} data_url
         * @private
         *
         */
        _generate_updated_url: function (data_url) {
            var updated_url = data_url.replace('recent', 'rss'),
        },

        /**
         * Given the api url just hit, update the rss link to match.
         *
         * This is the method the events call to perform the update.
         *
         * @method _update_url
         * @param {String} api_url
         * @private
         *
         */
        _update_url: function (api_url) {
            var link = this.get('rss_link');

            if (!link) {
                console.error('missing rss link');
            } else {
                link.setAttribute('href', this._generate_updated_url(api_url));
            }
        },

        initializer: function (cfg) {
            this._bind_events();
        }

    }, {
        ATTRS: {
            rss_link: {
                valueFn: function (val) {
                    return Y.one('#rss_url');
                }
            }
        }
    });



});
