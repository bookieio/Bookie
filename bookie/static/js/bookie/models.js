/**
 * Provide the models used for driving the various ui components
 *
 */
define(["bookie/main", "bookie/api"], function(main, api) {
    var models = {};

    models.Bmark = Backbone.Model.extend({

        initialize: function() {
            this.set({'dateinfo': this._dateinfo()});
            this.set({'prettystored': this._prettystored()});
        },

        allowedToEdit: function(account) {
            return true;
        },

        _dateinfo: function() {
            var t = new Date(this.get('stored'));
            return t.getMonth() + "/" + t.getDate();
        },

        /**
         * Builda date string of a pretty format
         * %m/%d/%Y %H:%M
         *
         */
        _prettystored: function () {
            var t = new Date(this.get('stored'));
            return t.getMonth() + "/" + t.getDate() + "/" + t.getFullYear() + " " +
                   t.getHours() + ":" + t.getMinutes();
        },

        /**
         * remove the bookmark using our api
         *
         */
        remove: function (success, error) {
            var callbacks = {
                'success': success,
                'error': error
            };

            api.remove(this.get('hash_id'), callbacks);
        }

    });


    /**
     * Handle keeping tabs on where we are as far as paging, results, etc
     *
     */
    models.PageControl = Backbone.Model.extend({
        // we'll set some defaults for the fields, 50 per page and starting on page
        // 0
        defaults: {
            "count":  50,
            "page":   0,
            "tags":   []
        },

        /**
         * Given the current config/url info stringify for html5 history
         *
         * url path should be current url + /tags/tags/?count=&page=
         * @todo need to bring in the underscore.string module for sprintf fun
         *
         *
         */
        to_url: function () {
            return _.sprintf("?count=%d&page=%d",
                              this.get('count'),
                              this.get('page'));
        }
    });


    /**
     * COLLECTIONS
     *
     */
    models.BmarkList = Backbone.Collection.extend({
        model: models.Bmark,
        cont: '.data_list',
        bmark_views: [],
        systemwide: false,

        /**
         * Empty the current bookmark list when required
         *
         * e.g. a page of new results coming
         *
         */
        empty: function () {
            _.invoke(this.bmark_views, 'remove');
            this.bmark_views = [];
        },

        fetch: function (page_control, callback) {
                var that = this;

                api.recent(page_control.toJSON(), {
                    'success': function (data) {
                        // remove the existing rows from the table
                        that.empty();

                        model_list = [];
                        _.each(data.bmarks, function (d) {
                            var m = new models.Bmark(d);
                            model_list.push(m);
                            // that.bmark_views.push(new ui.BmarkRow({'model': m}));
                        });

                        // @todo update this to a proper view for controlling/updating the
                        // count with the pagination info we want to display
                        $('.count').html(data.count);
                        $('.bmark').bind('mouseover', function (ev) {
                            $(this).find('.item').css('display', 'block');
                        }).bind('mouseout', function (ev) {
                            $(this).find('.item').css('display', 'none');
                        });

                        // handle the callback we're told to run once we've update
                        // the listings
                        if (callback !== undefined) {
                            callback();
                        }
                    },
                    'error': function (data, error_str) {
                        alert('error');
                    }
                }, this.systemwide);
        }
    });

    return models;
});
