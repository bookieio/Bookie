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

        /**
         * Make the call to remove the bookmark
         * Event constant and the event handler function
         *
         */
        'DELETE': 'delete',
        'ondelete': function (ev) {
            var url = $('#url').attr('value');
            var api_key = $('#api_key').attr('value');
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
        $b.call.getBookmark(url, function (xml) {
            var result, code, found;
            // this could come back as not found
            result = $(xml).find("result");

            $b.log('form base');
            $b.log(url);

            if (result.length > 0) {
                code = result.attr("code");
                $b.log('Page is not currently bookmarked')
            }

            found = $(xml).find("post");

            found.map(function () {
                // add the tags to the tag ui
                $('#tags').val($(this).attr('tag'));
                $('#tags').change();

                // add the description to the ui
                $('#description').val($(this).attr('description'));

                // add the description to the ui
                $('#extended').val($(this).attr('extended'));

                // now enable the delete button in case we want to delete it
                $b.ui.enable_delete();

            });

        });
    };


    // bookie methods
    $b.init = function (callback) {

        $b.log('in init');
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
            'api_key': $('#api_key').attr('value'),
            'description': $('#description').val(),
            'tags': $('#tags').val(),
            'extended': $('#extended').val(),
            'content': $('#content').val()
        }

        $b.call.saveBookmark(data);
        if (ev !== undefined) {
            ev.preventDefault();
        }
    };

    /**
     * Generate the get reuqest to the API call
     *
     */
    function request(options) {
        var defaults, opts;

        defaults = {
            type: "POST",
            dataType: "xml",
            context: $b,
            timeout: 30000,
            error: function(jqxhr, textStatus, errorThrown) {
                $b.log('REQUEST_ERROR');
                $b.log('Response Code: ' + jqxhr.status);
                $b.ui.notify(new Notification(
                    "error",
                    $b.response_codes[jqxhr.status],
                    textStatus,
                    "Could not find Bookie instance at " + $b.settings.get('api_url')));
            }
        };

        opts = $.extend({}, defaults, options);
        $.ajax(opts);
    };


    /*
     * Check if this is an existing bookmark
     * see http://delicious.com/help/api#posts_get
     *
     */
    $b.call.getBookmark = function (url, callback) {
        $b.log('in get bookmark');
        $b.api.bookmark($b.utils.hash_url(url), {
                    'success': function (data) {
                        if (data.success == true) {
                            if(callback) {
                                callback(xml);
                            }
                        } else {
                            $b.log('Error on get bookmark');
                            $b.log(data);
                        }
                    }
                });
    };


    $b.call.saveBookmark = function (params) {
        $b.log('saving bookmark');

        // we need to add the api key to the params
        params['api_key'] = $b.settings.get('api_key');
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
                    },
                });
    };


    /*
     * remove an existing bookmark from delicious
     * see http://delicious.com/help/api#posts_delete
     *
    */
    $b.call.removeBookmark = function (url, api_key, callback) {
        var opts = {
            url: $b.settings.get('api_url') + "/delapi/posts/delete",
            data: {
                url: url,
                api_key: api_key
            },

            success: function (xml) {
                var result, code;

                result = $(xml).find("result");
                code = result.attr("code");

                if (code == "done") {
                    $b.ui.notify(new Notification(
                        "info",
                        200,
                        $b.response_codes[code],
                        "Deleted"));
                } else {
                    // need to notify http://www.semiww.org/forum/memberlist.php?mode=viewprofile&u=5834that it failed
                    $b.ui.notify(new Notification(
                        "error",
                        400, //TODO: correctly determine http status code
                        $b.response_codes[code],
                        "Could not delete bookmark"));
                }
            }
        };

        request(opts);
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
