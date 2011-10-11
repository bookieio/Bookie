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

    main.login = {
        'init': function () {
            // we need to bind the api key show click
            $('#show_forgotten').bind('click', main.login.show_forgotten);
            $('#submit_forgotten').bind('click', main.login.submit_forgotten);
        },

        'show_forgotten': function (ev) {
            var $show = $('#forgotten_password');
            ev.preventDefault();

            // if the api key is showing and they click this, hide it
            if($show.is(':visible')) {
                $show.hide('fast');
            } else {
                $show.show(400);
            }
        },

        'clear': function () {
            $('#email').val("");
        },

        'message': function (msg, is_success) {
            var $msg = $('#forgotten_msg');
            $msg.html(msg);

            if (is_success) {
                $msg.attr('class', 'success');
            } else {
                $msg.attr('class', 'error');
            }

            $msg.show('slow');
        },

        'submit_forgotten': function (ev) {
            var email;
            ev.preventDefault();

            email = $('#email').val();

            main.api.reactivate({'email': email}, {
                'success': function (data)  {
                    main.login.clear();
                    main.login.message(data.message, true);
                }, 
                'error': function (data, error_string) {
                    console.log(data);
                    console.log(error_string);
                }
            });
        }
    };

    main.accounts = {
        'init': function () {
            // we need to bind the api key show click
            $('#show_key').bind('click', main.accounts.show_api_key);
            $('#show_bookmarklet').bind('click', main.accounts.show_bookmarklet);
            main.accounts.passwordui.init();
            main.accounts.updateui.init();
        },

        'show_api_key': function (ev) {
            var $key_div = $('#api_key'),
                $key_container = $('#api_key_container');

            ev.preventDefault();

            // if the api key is showing and they click this, hide it
            if($key_container.is(':visible')) {
                $key_container.hide('fast');
            } else {
                // make an ajax request to get the api key for this user and then
                // show it in the container for it
                main.api.api_key({
                    'success': function (data) {
                        $key_div.html(data.api_key);
                        $key_container.show(400);
                    }
                });
            }
        },

        'show_bookmarklet': function (ev) {
            var main = $('#bookmarklet_text');
            ev.preventDefault();

            // if the api key is showing and they click this, hide it
            if(main.is(':visible')) {
                main.hide('fast');
            } else {
                main.show(400);
            }
        },

        'updateui': {
            'init': function () {
                $('#submit_account_change').bind('click', main.accounts.updateui.change);
            },

            'change': function (ev) {
                ev.preventDefault();
                main.accounts.updateui.clear();

                main.api.account_update(
                    {
                        'name': $('#name').val(),
                        'email': $('#email').val()
                    },
                    {
                        'success': function (data) {
                            main.accounts.updateui.message("Account updated", true);
                         },
                        'error': function (data, data_msg) {
                            console.log(data);
                            console.log(data_msg);
                        }
                    });
            },

            'clear': function () {
                $('#account_msg').hide('fast');
            },

            'message': function (msg, is_success) {
                var $msg = $('#account_msg');
                $msg.html(msg);

                if (is_success) {
                    $msg.attr('class', 'success');
                } else {
                    $msg.attr('class', 'error');
                }

                $msg.show('slow');
            }
        },

        'passwordui': {
            'init': function () {
                $('#show_password').bind('click', main.accounts.passwordui.show);
                $('form#password_reset').bind('submit', main.accounts.passwordui.change);
                $('#submit_password_change').bind('click', main.accounts.passwordui.change);
            },

            'show': function (ev) {
                var $div = $('#password_change');

                ev.preventDefault();

                if ($div.is(':visible')) {
                    $div.hide('fast');
                } else {
                    $div.show(400);

                }
            },

            'reset': function () {
                $('#current_password').val("");
                $('#new_password').val("");
                $('#password_change').hide();
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

                // hide the current message window
                $('#password_msg').hide('fast');

                main.api.change_password( {
                        'current_password': $('#current_password').val(),
                        'new_password': $('#new_password').val()
                    },
                    {
                        'success': function (data) {
                            main.accounts.passwordui.message(data.message, true);
                            main.accounts.passwordui.reset();
                         },
                        'error': function (data, status_string) {
                            main.accounts.passwordui.message(data.error, false);
                            main.accounts.passwordui.reset();
                        }
                    }
                );
            }
        }
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
