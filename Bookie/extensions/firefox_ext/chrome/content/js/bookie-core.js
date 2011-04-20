/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

//If this wrapper isn't here, the jQuery syntax inside doesn't work.  You can't include jquery.js in the .xul
//definition, as it breaks the toolbar buttons.  This wrapper is a standard feature of solutions found via google.

window.addEventListener("load", function(event){
    (function(loader){
        loader.loadSubScript("chrome://bookie/content/js/jquery.min.js");
    })(
        Components.classes["@mozilla.org/moz/jssubscript-loader;1"].getService(
            Components.interfaces.mozIJSSubScriptLoader
        )
    );

    var jQuery = window.jQuery.noConflict(true);

    /* chrome-extension-specific bookie functionality */

   var bookie = (function (module, $) {

        module.aConsoleService = Components.classes["@mozilla.org/consoleservice;1"].getService(Components.interfaces.nsIConsoleService);
        // This works here just fine.  And if later you use the aConsoleService attribute, it works fine.
        module.aConsoleService.logStringMessage('Creating bookie in bookie-core');

        // bootstrap some custom things that the extensions will jump in on
        module.ui = {};
        module.call = {};

        // some constants we'll use throughout
        // dom hook for triggering/catching events fired
        module.EVENTID = '#bmarkbody';

        /**
         * Define events supported
         * Currently we've got LOAD, SAVED, ERROR, DELETE, UPDATE
         *
         */
        module.events = {
            'LOAD': 'load',
            'onload': function (ev) {
                $('#tags').focus();
                $('#form').bind('submit', function (ev) {
                    var data = $(this).serialize();
                    module.call.saveBookmark(data);
                    ev.preventDefault();
                });

                module.populateForm();
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
                module.call.removeBookmark(url, api_key);
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
        module.response_codes = {
            // http status codes returned
            '200': 'Ok',
            '403': 'NoAuth',
            '404': '404',

            // some codes from the xml response in the delicious api
            'done': 'Ok',
            'Not Found': '404',
            'Bad Request: missing url': 'Err',
        };

        function Notification(type, code, shortText, longText)
        {
            this.type = type;
            this.code = code;
            this.shortText = shortText;
            this.longText = longText;
        }

        /**
         * The actual work to map the tab object data ot the form ui
         * This is shared across platforms as we want to keep the ui/code
         * consistent between them
         *
         */
        module.populateFormBase = function (tab_obj) {
            var url;

            $('#url').val(tab_obj.url);
            $('#description').val(tab_obj.title);
            $('#api_key').val(localStorage['api_key']);

            url = $('#url').attr('value');

            module.call.getBookmark(url, function (xml) {
                var result, code, found;
                // this could come back as not found
                result = $(xml).find("result");

                if (result.length > 0) {
                    code = result.attr("code");
                    console.log('Page is not currently bookmarked')
                    // we don't update the badge, since this happens on every page
                    // we load our ui from, it's not an error to not be found
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
                    module.ui.enable_delete();

                });

            });
        };

        // bookie methods
        module.init = function () {
            if (!localStorage['api_url']) {
                console.log('No API URL');
                module.ui.notify(new Notification('error', 0, 'No URL', 'Bookie URL has not been set'));
                return;
            }

            // what url are we sending out requests off to?
            module.api_url = localStorage['api_url'];

            $(module.EVENTID).bind(module.events.LOAD, module.events.onload);
            $(module.EVENTID).trigger(module.events.LOAD);
        };

        // cross platform ui calls
        module.ui.enable_delete = function (ev) {
            // show the button and bind the event to fire the delete off
            $('#delete').show().bind('click', function (ev) {
                $(module.EVENTID).trigger(module.events.DELETE);
            });

            // and make sure we bind the delete event
            $(module.EVENTID).bind(module.events.DELETE, module.events.ondelete);
        };


        /**
         * Generate the get reuqest to the API call
         *
         */
        function request(options) {
            var defaults, opts;

            defaults = {
                type: "GET",
                dataType: "xml",
                error: function(jqxhr, textStatus, errorThrown) {
                    module.ui.notify(new Notification(
                        "error",
                        module.response_codes[jqxhr.status],
                        textStatus,
                        "Could not find Bookie instance at " + module.api_url));
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
        module.call.getBookmark = function (url, callback) {
            var opts = {
                url: module.api_url + "/delapi/posts/get",
                data: {url: url},
                success: function (xml) {
                    console.log('done, looking for callback');

                    if(callback) {
                        callback(xml);
                    }
                }
            };

            request(opts);
        };

        module.call.saveBookmark = function (params) {
            var opts;

            opts = {
                url: module.api_url + "/delapi/posts/add",
                data: params,
                success: function(xml) {
                    var result, code;
                    result = $(xml).find("result");

                    code = result.attr("code");

                    if (code == "done") {
                        module.ui.notify(new Notification(
                            "info",
                            200,
                            module.response_codes[code],
                            "saved"));
                    } else {
                        // need to notify that it failed
                        module.ui.notify(new Notification(
                            "error",
                            400, //TODO: correctly determine http status code
                            module.response_codes[code],
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
        module.call.removeBookmark = function (url, api_key) {
            var opts = {
                url: module.api_url + "/delapi/posts/delete",
                data: {
                    url: url,
                    api_key: api_key
                },

                success: function (xml) {
                    var result, code;

                    result = $(xml).find("result");
                    code = result.attr("code");

                    if (code == "done") {
                        module.ui.notify(new Notification(
                            "info",
                            200,
                            module.response_codes[code],
                            "Deleted"));
                    } else {
                        // need to notify that it failed
                        module.ui.notify(new Notification(
                            "error",
                            400, //TODO: correctly determine http status code
                            module.response_codes[code],
                            "Could not delete bookmark"));
                    }
                }
            };

            request(opts);
        };

        return module;
    })(bookie || {}, jQuery);

}, false);
