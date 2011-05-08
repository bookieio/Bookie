/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

/* chrome-extension-specific bookie functionality */

var bookie = (function (module, $, logger) {
    // shortcut bookie. (module) to just $b
    $b = module;

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


    // stash the logger onto $b for FF to use and
    $b.log = logger.log;

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

                // add the description to the ui
                $('#description').val($(this).attr('description'));

                // add the description to the ui
                $('#extended').text($(this).attr('extended'));

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

        $b.log('IN SUBMIT EVENT');
        data = {
            'url': $('#url').attr('value'),
            'api_key': $('#api_key').attr('value'),
            'description': $('#description').val(),
            'tags': $('#tags').val(),
            'extended': $('#extended').val()
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

        var opts = {
            url: $b.settings.get('api_url') + "/delapi/posts/get",
            data: {
                'url': url
            },
            success: function (xml) {
                $b.log('GET BOOKMARK');
                $b.log(callback);
                if(callback) {
                    callback(xml);
                }
            }
        };

        request(opts);
    };


    $b.call.getTagCompletions = function (tag, callback) {
        var opts = {
            url: $b.settings.get('api_url') + "/delapi/tags/complete",
            data: {tag: tag},
            success: function (xml) {
                alert("got xml: " + xml);

                if(callback) {
                    callback(xml);
                }
            }
        };

        request(opts);
    }


    $b.call.saveBookmark = function (params) {
        var opts;

        // we need to add the api key to the params
        params['api_key'] = $b.settings.get('api_key');

        opts = {
            url: $b.settings.get('api_url') + "/delapi/posts/add",
            data: params,
            success: function(xml) {
                var result, code;
                result = $(xml).find("result");

                code = result.attr("code");

                if (code == "done") {
                    $b.ui.notify(new Notification(
                        "info",
                        200,
                        $b.response_codes[code],
                        "saved"));
                } else {
                    // need to notify that it failed
                    $b.ui.notify(new Notification(
                        "error",
                        400, //TODO: correctly determine http status code
                        $b.response_codes[code],
                        "Could not save bookmark"));
                }
            },
        };

        request(opts);
    }


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
                    // need to notify that it failed
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


    /*
     * fetch a set of completion options
     * Used for completing tag names in the extension
     *
    */
    $b.call.tagComplete = function (substring, callback) {
        var opts = {
            url: $b.settings.get('api_url') + "/delapi/tags/complete",
            type: "GET",
            data: {
                tag: substring
            },

            success: function (xml) {
                $b.log('success call to complete');
                tag_list = [];
                results = $(xml).find("tag");
                results.map(function () {
                    tag_list.push($(this).text());
                });

                callback(tag_list);
            }
        };

        request(opts);
    };


    return $b;

})(bookie || {}, jq_var, logger);
