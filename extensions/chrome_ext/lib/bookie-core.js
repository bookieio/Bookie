/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

/* chrome-extension-specific bookie functionality */

var bookie = (function (opts) { //module, $, logger) {
    // shortcut bookie. (module) to just $b
    var $b = opts.bookie,
        $ = opts.jquery;

    $b.log = opts.console_log.log;  // stash the logger onto $b for FF to use and

    // bootstrap some custom things that the extensions will jump in on
    $b.ui = {};
    $b.call = {};

    // some constants we'll use throughout
    // dom hook for triggering/catching events fired
    $b.EVENTID = '#bmarkbody';

    /**
     * Define events supported
     * Currently we've got LOAD, SAVED, ERROR, DELETE, UPDATE
     *
     */
    $b.events = {
        'LOAD': 'load',
        'onload': function (ev, current_tab_info) {
            $b.log('in onload event');
            $('#tags').focus();
            $('#form').bind('submit', $b.store_changes);
            $b.populateForm(current_tab_info);
        },

        'SAVE': 'save',
        'ERROR': 'error',
        'DUPE_TAGS': 'dupe_tags',

        /**
         * Make the call to remove the bookmark
         * Event constant and the event handler function
         *
         */
        'DELETE': 'delete',
        'ondelete': function (ev) {
            var url = $('#url').attr('value'),
                api_key = $('#api_key').attr('value');
            $b.call.removeBookmark($b.utils.hash_url(url));
            ev.preventDefault();
        },

        'UPDATE': 'update'
    };

    /**
     * The server can respond to request with a number of success/error codes. We
     * want to provide a common mapping from application to client side code so
     * that we can provide a decent notification to the user
     *
     */
    $b.response_codes = {
        // http status codes returned
        '200': 'Ok',
        '403': 'NoAuth',
        '404': '404',

        'syn': 'Sync',
        // some codes from the xml response in the delicious api
        'done': 'Ok',
        'Not Found': '404',
        'Bad Request: missing url': 'Err',
    };


    function Notification(type, code, shortText, longText) {
        this.type = type;
        this.code = code;
        this.shortText = shortText;
        this.longText = longText;
    }

    // I need this to create a notification object from the bookie.chrome.js
    // file
    $b.Notification = Notification;

    // API for accessing setting information
    // this needs to be implemented on the -chrome and -firefox files
    $b.settings = {
        'init':function () {
            $b.log('not implemented init');
        },
        'get': function (key) {
            $b.log('not implemented get');
        },
        'set': function (key) {
            $b.log('not implemented set');
        }
    };


    /**
     * The actual work to map the tab object data ot the form ui
     * This is shared across platforms as we want to keep the ui/code
     * consistent between them
     *
     */
    $b.populateFormBase = function (tab_obj, inserted_by) {
        var url;

        $('#url').attr('value', tab_obj.url);
        $('#description').attr('value', tab_obj.title);
        $('#api_key').attr('value', $b.settings.get('api_key'));
        // is this coming from the chrome extension, firefox, elsewhere?
        $('#inserted_by').attr('value', inserted_by);

        url = $('#url').attr('value');

        // start out the extended as empty in case we had an old value
        $('#extended').val("");

        $b.log('populate form base');
        $b.call.getBookmark(url, function (data) {
            var result, code, found, tags, bmark;
            tags = [];
            bmark = data.bmark;

            for (tg in bmark.tags) {
                tags.push(bmark.tags[tg].name);
            }

            $('#tags').val(tags.join(" "));
            $('#tags').change();

            // add the description to the ui
            $('#description').val(bmark.description);

            // add the description to the ui
            $('#extended').val(bmark.extended);

            // now enable the delete button in case we want to delete it
            $b.ui.enable_delete();

        }, function (data, status_string) {
            $b.log('Page is not currently bookmarked');

            // see if we have the last set of tags to add
            if (data.hasOwnProperty('last')) {
                var tag_str = data.last.tag_str,
                    tags = tag_str.split(' '),
                    tag_html;

                for (tag in tags) {
                     tags[tag] = '<a href="" class="prev_tag">' + tags[tag] + '</a>';
                }

                $('#latest_tags').append(tags.join(" ")).show();

                $("table").delegate("td", "hover", function(){
                    $(this).toggleClass("hover");
                });
            }
        });
    };


    // bookie methods
    $b.init = function (callback, callback_data) {
        $b.settings.init();

        if (!$b.settings.get('api_url') || !$b.settings.get('api_username')) {
            $b.log('No API url or Username.');
            $b.ui.notify(new Notification('error', 0, 'No url or username', 'Bookie URL info has not been set'));
        } else {
            $b.api.init($b.settings.get('api_url'),
                        $b.settings.get('api_username'),
                        $b.settings.get('api_key'));

            // allow for the browser specific plugins to do some custom init
            if (callback_data !== undefined) {
                callback(callback_data);
            } else {
                callback();
            }
        }
    };


    // cross platform ui calls
    $b.ui.enable_delete = function (ev) {
        // show the button and bind the event to fire the delete off
        $('#delete').show().bind('click', function (ev) {
            $($b.EVENTID).trigger($b.events.DELETE);
        });

        // and make sure we bind the delete event
        $($b.EVENTID).bind($b.events.DELETE, $b.events.ondelete);
    };


    $b.store_changes = function (ev) {
        var data, ext_val;

        if (ev !== undefined) {
            ev.preventDefault();
        }

        data = {
            'url': $('#url').attr('value'),
            'description': $('#description').val(),
            'tags': $('#tags').val(),
            'extended': $('#extended').val(),
            'content': $('#content').val()
        };

        $b.call.saveBookmark(data);
        if (ev !== undefined) {
            ev.preventDefault();
        }
    };


    /*
     * Check if this is an existing bookmark
     * see http://delicious.com/help/api#posts_get
     *
     */
    $b.call.getBookmark = function (url, success_callback, fail_callback) {
        $b.api.bookmark($b.utils.hash_url(url), {
                    'success': function (data) {
                        if(success_callback) {
                            success_callback(data);
                        }
                    },
                    'error': function (data, status_string) {
                        console.log('bookmark not found: ' + url);
                        if (fail_callback) {
                            fail_callback(data);
                        }
                    }
                }, true);
    };


    $b.call.saveBookmark = function (params) {
        // we need to add the api key to the params
        console.log(params);
        $b.api.add(params, {
                   'success': function (data) {
                        $b.ui.notify(new Notification(
                            "info",
                            200,
                            $b.response_codes[data.message],
                            "saved"));
                   },
                    'error': function (data, status_string) {
                        // if there's an error, say a 403 or something display
                        // an error
                        $b.ui.notify(new Notification(
                            "error",
                            status_string, //TODO: correctly determine http status code
                            $b.response_codes[status_string],
                            "Could not save bookmark. Please check error code."));
                    }
                });
    };


    $b.call.read_later = function (url, description, content) {
        var data = {
                'url': url,
                'tags': "!toread",
                'description': description,
                'api_key': $b.settings.get('api_key')
        };

        if (content !== undefined) {
            data.content = content;
        }

        $b.api.add(data, {
                'success': function (data) {
                    if (data.success === true) {
                        $b.ui.notify(new Notification(
                            "info",
                            200,
                            $b.response_codes[data.message],
                            "saved"));
                    } else {
                        // need to notify that it failed
                        $b.ui.notify(new Notification(
                            "error",
                            400, //TODO: correctly determine http status code
                            $b.response_codes[data.message],
                            "Could not save bookmark"));
                    }
                },

                'error': function (jqxhr, textStatus, errorThrown) {
                    // if there's an error, say a 403 or something display
                    // an error
                    $b.ui.notify(new Notification(
                        "error",
                        jqxhr.status, //TODO: correctly determine http status code
                        $b.response_codes[jqxhr.status],
                        "Could not save bookmark. Please check error code."));
                }

            }
        );
    };


    /*
     * remove an existing bookmark from delicious
     * see http://delicious.com/help/api#posts_delete
     *
    */
    $b.call.removeBookmark = function (hash_id) {
        $b.api.remove(hash_id, {
             'success': function (data) {
                $b.ui.notify(new Notification(
                    "info",
                    200,
                    $b.response_codes[data.message],
                    "Deleted"));
             },
             'error': function (data, status_string) {
                    $b.ui.notify(new Notification(
                        "error",
                        400, //TODO: correctly determine http status code
                        $b.response_codes[data.error],
                        "Could not delete bookmark"));
             }
        });
    };


    $b.call.getTagCompletions = function (tag, callback) {
        var success = function (data) {
                        callback(data.tags);
                      };

        $b.api.tag_complete(tag, undefined, {
                                'success': success
                            });
    };


    return $b;

})(bookie_opts);
// object = 'bookie', 'jquery', 'console.log'
