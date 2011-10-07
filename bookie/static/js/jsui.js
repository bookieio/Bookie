/**
 * Provide tools to do a backbone driven ui
 *
 */
var bookie = (function ($b, $) {

    // bookie.backbone
    $b.bb = {};

    /**
     * MODELS
     *
     */
    $b.bb.Bmark = Backbone.Model.extend({

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

            bookie.api.remove(this.get('hash_id'), callbacks);
        }

    });


    /**
     * Handle keeping tabs on where we are as far as paging, results, etc
     *
     */
    $b.bb.Control = Backbone.Model.extend({
        // we'll set some defaults for the fields, 50 per page and starting on page
        // 0
        defaults: {
            "count":  50,
            "page":   0,
            "tags":   []
        },

        /**
         * Read in the values for the default page/counts/tags from the url in case
         * someone sends/bookmarks a url. Should tie into our use of history.js
         * somehow
         *
         */
        url_load: function() {

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
            return "?count=" + this.get('count') + "&page=" + this.get('page');
        }
    });


    /**
     * COLLECTIONS
     *
     */
    $b.bb.BmarkList = Backbone.Collection.extend({
        model: $b.bb.Bmark,
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

                bookie.api.recent(page_control.toJSON(), {
                    'success': function (data) {
                        // remove the existing rows from the table
                        that.empty();

                        model_list = [];
                        _.each(data.bmarks, function (d) {
                            var m = new $b.bb.Bmark(d);
                            model_list.push(m);
                            that.bmark_views.push(new $b.bb.BmarkRow({'model': m}));
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

    /**
     * VIEW
     *
     */
    $b.bb.BmarkRow = Backbone.View.extend({

        tagName: 'div',
        className: 'bmark',
        parent: '.data_list',

        initialize: function() {
            this.render();
        },

        events: {
          "click .delete":          "delete",
          // "click .button.edit":   "openEditDialog",
          // "click .button.delete": "destroy"
        },

        render: function() {
            // Compile the template using underscore
            var template = _.template($("#bmark_row").html(), this.model.toJSON());

            // Load the compiled HTML into the Backbone "el"
            //     var template = $("#category_tpl").tmpl(this.model.toJSON());
            $(this.el).html(template).attr('id', this.model.get('hash_id'));
            $(this.parent).append(this.el);
        },

        /**
         *
         * We want to make sure that they're sure they want it gone
         *
         */
        delete: function (ev) {
            ev.preventDefault();
            var answer = confirm ("Are you sure you want to delete the bookmark."),
                that = this,
                success = function (data) {
                    that.remove();
                };

            if (answer) {
                // make the model call to delete
                this.model.remove(success);
            } else {
                // then leave it alone
            }
        }

    });


    /**
     * Control the events and updates from paging and such
     *
     */
    $b.bb.ControlView = Backbone.View.extend({
        cont: '.controls',
        init: true,
        username: undefined,

        initialize: function() {
            var that = this;
            this.$el = $(this.cont);

            this.bmark_list = new $b.bb.BmarkList();

            // if we don't provide a username, it's systemwide scope
            // else we're in the user scope which is the default
            if (this.options.username === undefined) {
                this.bmark_list.systemwide = true;
            }

            this.bmark_list.fetch(this.model, function () {
                that.show_buttons();
            });

            this.model.bind('change', function (ev) {
                // add the callback to show the controls updated after the
                // successful fetching of new data
                that.bmark_list.fetch(that.model, function() {
                    that.show_buttons();
                });
            });

            // Bind to popstate event
            History.Adapter.bind(window, 'popstate', function(ev) {
                var prev_state = History.getState();

                // if it's empty, don't update anything
                if (prev_state.data['page'] === undefined) {
                    if (that.init) {
                        // push the current data set
                        History.pushState(that.model.toJSON(), "", that.model.to_url());
                    } else {
                        History.back();
                    }
                } else {
                    // Note: We are using statechange instead of popstate
                    that.model.set(prev_state.data);
                }

                // the first time we go through here, flip the init state on our
                // ControlView. This let's us detect that we're "back" on the first
                // page and should allow the browser's back to kick into effect
                that.init = false;

            });
        },

        events: {
            "click a.next":         "next_page",
            "click a.previous":     "previous_page"
        },

        next_page: function (ev) {
            ev.preventDefault();
            var cur = this.model.get('page');
            this.model.set({'page': cur + 1});

            var current_model = this.model.toJSON();
            History.pushState(current_model,
                              "Bookmarks Page: " + (this.model.get('page') + 1),
                              this.model.to_url());
        },

        previous_page: function (ev) {
            ev.preventDefault();
            var cur = this.model.get('page');
            this.model.set({'page': cur - 1});

            var current_model = this.model.toJSON();
            History.pushState(current_model,
                              "Bookmarks Page: " + (this.model.get('page') + 1),
                              this.model.to_url());

        },

        /**
         * Control what buttons we display based on current page
         *
         * if on page 0, then don't show prev
         * if there are no more results, then don't show next
         *
         * We've got 2 edge cases:
         *     page 0 shows no prev
         *     page $MAX shows no next
         *
         */
        show_buttons: function () {
            if (this.model.get('page') === 0) {
                $('.previous').remove();
            }

            if (this.model.get('page') !== 0) {
                this._show_prev();
            }

            // we've hit the max if the number of results we have is less than the
            // number we asked for
            if (this.model.get('count') > this.bmark_list.bmark_views.length) {
                // hide the next button
                $('.next').remove();
            } else {
                // then show the nexte button if it's not already there
                this._show_next();
            }
        },

        /**
         * Add the previous button if required
         *
         */
        _show_prev: function () {
            // only add if it's not already there
            if (!!this.$el.find('.previous').length === false) {
                var template = _.template($("#previous_control").html());
                this.$el.find('.paging').prepend(template);
            }
        },

        /**
         * Add the next button if required
         *
         */
        _show_next: function () {
            // only add if it's not already there
            if (!!this.$el.find('.next').length === false) {
                var template = _.template($("#next_control").html());
                this.$el.find('.paging').append(template);
            }
        }

    });

    return $b;
})(bookie || {}, jQuery);
