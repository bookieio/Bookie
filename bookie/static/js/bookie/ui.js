/**
 * Provide tools to do a backbone driven ui
 *
 * :require: main and model files since our ui is bound do model and using
 * events/etc from main
 *
 */
define(["bookie/main", "bookie/models", "bookie/api"], function(main, models, api) {
    var ui = {};

    /**
     * We'll use this to load extra CSS files we must have for things in the UI
     *
     */
    ui.loadcss = function loadCss(url) {
        var link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = url;
        document.getElementsByTagName("head")[0].appendChild(link);
    };


    ui.filterui = {
        id: '',
        init: function () {
            var that = this;
            ui.loadcss('/static/css/chosen.css');
            // $(".chzn-select").chosen();
            // $(".chzn-select").parent().delegate('input', 'keyup', function(ev) {
            //     console.log($(this).val());
            //     that.update_completion($(this).val());
            // });

            $(".chzn-select").ajaxChosen({
                        method: 'GET',
                        url: '/api/v1/admin/tags/complete',
                        dataType: 'json'
                    }, function (data) {
                        var terms = {};

                        $.each(data.tags, function (i, val) {
                            terms[i] = val;
                        });

                        return terms;
            });
        },
        update_completion: function (val) {
            if (val.length < 3) {
                return;
            }
            var options = {'tag': val, 'current': []},
                callbacks = {
                    'success': function (data) {
                        console.log(data.tags);
                        var options = _.reduce(data.tags, function (memo, tag) {
                            console.log(memo);
                            return memo += _.sprintf('<option value="%s">%s</option>', tag, tag);
                        }, "");

                        $(".chzn-select").find('option').each(function (node) {
                            if (!$(this).is(":selected")) {
                                $(this).remove()
                            }
                        }).append(options).trigger("liszt:updated");

                        $(this).parent().find('input').attr('value', val);
                    }
                };

            api.tag_complete(options, callbacks);
        }
    };

    ui.BmarkRow = Backbone.View.extend({

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
                return false;
            }
        }
    });


    /**
     * Control the events and updates from paging and such
     *
     */
    ui.ControlView = Backbone.View.extend({
        cont: '.controls',
        init: true,
        username: undefined,

        initialize: function() {
            var that = this;
            this.$el = $(this.cont);

            this.bmark_list = new models.BmarkList();

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

    return ui;
});
