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
        'onload': function (ev) {
            $b.log('in onload event');
            $('#tags').focus();
            $('#form').bind('submit', $b.store_changes);
            $b.populateForm();
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
            $b.call.removeBookmark(url, api_key);
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
    $b.populateFormBase = function (tab_obj) {
        var url;

        $('#url').attr('value', tab_obj.url);
        $('#description').attr('value', tab_obj.title);
        $('#api_key').attr('value', $b.settings.get('api_key'));

        url = $('#url').attr('value');

        // start out the extended as empty in case we had an old value
        $('#extended').val("");

        $b.log('populate form base');
        $b.call.getBookmark(url, function (data) {
            var result, code, found, tags, bmark;
            $b.log('form base');
            $b.log(url);

            tags = [];
            bmark = data.payload.bmark;

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

        }, function (data) {
            $b.log('Page is not currently bookmarked');

            // see if we have the last set of tags to add
            if (data.payload.hasOwnProperty('last')) {
                $('#latest_tags a').html(data.payload.last.tag_str).parent().show();
            }
        });
    };


    // bookie methods
    $b.init = function (callback) {
        $b.settings.init();

        if (!$b.settings.get('api_url')) {
            $b.log('No API URL');
            $b.ui.notify(new Notification('error', 0, 'No URL', 'Bookie URL has not been set'));
        } else {
            $b.log('no api url');
            // allow for the browser specific plugins to do some custom init
            $b.log(callback);
            callback();
        }

        console.log('initing the api code');
        $b.api.init($b.settings.get('api_url'));
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

        data = {
            'url': $('#url').attr('value'),
            'api_key': $b.settings.get('api_key'),
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
                        if (data.success === true) {
                            if(success_callback) {
                                success_callback(data);
                            }
                        } else {
                            console.log('bookmark not found: ' + url);
                            $b.log(data);
                            if (fail_callback) {
                                fail_callback(data);
                            }
                        }
                    }
                }, true);
    };


    $b.call.saveBookmark = function (params) {
        // we need to add the api key to the params
        params.api_key = $b.settings.get('api_key');
        $b.api.add(params,
                   {'success': function (data) {
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
                }
            }
        );
    };


    /*
     * remove an existing bookmark from delicious
     * see http://delicious.com/help/api#posts_delete
     *
    */
    $b.call.removeBookmark = function (url, api_key) {
        $b.api.remove(url, api_key, {
             success: function (data) {
                var result, code;

                if (data.message === "done") {
                    $b.ui.notify(new Notification(
                        "info",
                        200,
                        $b.response_codes[data.message],
                        "Deleted"));
                } else {
                    // need to notify http://www.semiww.org/forum/memberlist.php?mode=viewprofile&u=5834that it failed
                    $b.ui.notify(new Notification(
                        "error",
                        400, //TODO: correctly determine http status code
                        $b.response_codes[data.message],
                        "Could not delete bookmark"));
                }
            }
        });

    };


    $b.call.getTagCompletions = function (tag, callback) {
        var current_vals, current;

        // we need to get the current list of tags from the input field itself
        current_vals = $('#tags').val().split(" ");
        if (current_vals.length === 0) {
            current = [];
        } else {
            current = current_vals;
        }

        $b.api.tag_complete(tag,
                current,
                { 'success': function (data) {
                                   callback(data.payload.tags);
                             }
                }
        );
    };


    return $b;

})(bookie_opts);
// object = 'bookie', 'jquery', 'console.log'
