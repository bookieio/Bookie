/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */
define([], function () {
    var main = {};
    main.ui = {};

    // some constants we'll use throughout
    // dom hook for triggering/catching events fired
    main.EVENTID = 'body';

    // we expect the api init for us

    /**
     * Define events supported
     *
     */
    main.events = {
        'LOAD': 'load',
        'TAG_FILTER': 'tag_filter',
    };


    /**
     * Once the page is loaded, perform some nice basics we need
     *
     */
    main.load = function (ev) {
        // init the tag filter ui completion code
        $(main.EVENTID).trigger(main.events.TAG_FILTER);

        // if we're on the readable page, make sure we catch all links and
        // check if we should follow or not
        $('#readable_content a').bind('click', function (ev) {
            // grab the href value and check if it starts with http or www
            var url = $(this).attr('href'),
                original_url = "",
                newwindow;

            if (!_.startsWith(url, 'http') && !_.startsWith(url, 'www')) {
                // instead of this url, open the original web page instead of a
                // broken look into http://bookie/blah.html
                ev.preventDefault();
                original_url = $('.bmark').attr('href');
                newwindow = window.open(original_url, '_blank');

                newwindow.focus();
                return false;

            } else {
                // this will go well, just keep going and open the link
                return true;
            }
        });
    };


    /**
     * Control the tag filter ui on the main pages
     *
     */
    main.ui.init_tag_filter = function (ev) {
        var $tag_filter = $('#tag_filter');

        $tag_filter.superblyTagField({
            complete: function (tag, callback) {
                var current_vals, current;

                current_vals = $('#tag_filter').val().split(" ");
                if (current_vals.length === 0) {
                    current = [];
                } else {
                    current = current_vals;
                }

                main.api.tag_complete({
                        'tag': tag,
                        'current': current,
                        },
                        { 'success': function (data) {
                                           callback(data.tags);
                                     }
                        }
                );
            },
        });

        // fire off for existing tags
        // but only if we have a tag to pretty up
        if ($tag_filter.val()) {
            $('#tag_filter').change();
        }

        $('form#filter_form').bind('submit', function (ev) {
            ev.preventDefault();
            terms = $('#tag_filter').val().split(" ");
            url = APP_URL + "/recent/" + terms.join('/');
            window.location = url;
        });
    };


    // only need to call init on the page read event
    main.init = function (api_obj) {
        // we need the bookie api stuff
        main.api = api_obj;

        // make sure we bind the page load event
        $(main.EVENTID).bind(main.events.LOAD, main.load);

        // bind some other events we might want read to go out of the gates
        $(main.EVENTID).bind(main.events.TAG_FILTER, main.ui.init_tag_filter);

        // now trigger the load since we're ready to go from here
        $(main.EVENTID).trigger(main.events.LOAD);

    };


    main.reset = {
        'init': function () {
            $('#submit_password_change').bind('click', main.reset.change);
            $('form#password_reset').bind('submit', main.reset.change);
        },

        'message': function (msg, is_success) {
            var $msg = $('#password_msg');
            $msg.html(msg);

            if (is_success) {
                $msg.attr('class', 'success');
            } else {
                $msg.attr('class', 'error');
            }

            $msg.show('slow');
        },

        // Change the user's password, get the things together and visit the
        // api with the current password and new one
        'change': function (ev) {
            ev.preventDefault();

            console.log('calling activate');

            main.api.activate({
                    'username': $('#username').val(),
                    'code': $('#code').val(),
                    'password': $('#new_password').val(),
                },
                {
                    'success': function (data) {
                        main.reset.message(data.message, true);
                     },
                    'error': function (data, error_msg) {
                        console.log(data);
                        console.log(error_msg);
                    }
                }
            );
        }
    };

    main.edit = {
        'init': function () {
            this.bind_tag_complete();
            this.bind_tag_suggest();
        },

        'bind_tag_suggest': function () {
            $('#tag_suggest').delegate('a', 'click', function (ev) {
                ev.preventDefault();
                main.edit.dupe_tags($(this));
            });
        },

        /**
         * Copy any tags we have from the last run into our tags ui
         *
         */
        'dupe_tags': function (node) {
            var current = $('#tags').val().trim();
            if (current.length > 0) {
                current = current + " ";
            }

            $('#tags').val(current + node.html().trim());
            $('#tags').change();
            node.remove();

            // if we've added all the tags and there are none left, then just hide
            // that div
            if ($("#tag_suggest a").length === 0) {
                $('#tag_suggest').parent().hide();
            }
        },

        'bind_tag_complete': function () {
            var $tag_filter = $('#tags');

            $tag_filter.superblyTagField({
                complete: function (tag, callback) {
                    main.api.tag_complete({
                            'tag': tag
                            },
                            { 'success': function (data) {
                                             callback(data.tags);
                                         }
                            }
                    );
                },
            });

            // fire off for existing tags
            // but only if we have a tag to pretty up
            if ($tag_filter.val()) {
                $('#tags').change();
            }
        }

    };

    return main;
});
