/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

var bkg = chrome.extension.getBackgroundPage();

/*
 * api for interacting with delicious
 * see http://delicious.com/help/api
*/
var delicious;

if (!delicious) {
    delicious = {};
}

// https://api.del.icio.us/v1/
delicious.api_url = 'http://127.0.0.1:6543/delapi/';
//delicious.api_url = 'http://rick.bmark.us/delapi/';


/**
 * Generate the get reuqest to the API call
 *
 */
delicious._request = function (options) {
    var defaults, opts;

    defaults = {
        type: "GET",
        dataType: "xml",
        // username: localStorage['username'],
        // password: localStorage['password'],
        error: onerror
    };

    opts = $.extend({}, defaults, options);
    $.ajax(opts);
};


/*
 * save a new bookmark to delicious.
 * if bookmark already exists for this url, the existing one will be updated
 * see http://delicious.com/help/api#posts_add
 *
*/
delicious.savebookmark = function (params, options) {
    var defaults, opts;

    defaults = {
        url: delicious.api_url + "posts/add",
        data: params,
        success: function (xml) {
            var result, code;

            result = $(xml).find("result");
            code = result.attr("code");

            if (code == "done") {
                console.log("Bookmark saved to delicious!");
            } else {
                chrome.browserAction.setBadgeText({text: code});
                console.error("Error saving bookmark: " + code);
            }
        }
    };

    opts = $.extend({}, defaults, options);
    delicious._request(opts);
};

/*
 * remove an existing bookmark from delicious
 * see http://delicious.com/help/api#posts_delete
 *
*/
delicious.removebookmark = function (url, api_key) {
    var opts = {
        url: delicious.api_url + "posts/delete",
        data: {
            url: url,
            api_key: api_key
        },
        success: function (xml) {
            var result, code;

            result = $(xml).find("result");
            code = result.attr("code");

            if (code == "done") {
                window.close();

            } else {
                chrome.browserAction.setBadgeText({text: code});
                console.error("Error removing bookmark: " + code);
            }
        }
    };

    delicious._request(opts);
};


/*
 * Check if this is an existing bookmark
 * see http://delicious.com/help/api#posts_get
 *
*/
delicious.getbookmark = function (url, callback) {
    var opts = {
        url: delicious.api_url + "posts/get",
        data: {url: url},
        success: function (xml) {


            $(xml).find("post").map(function () {
                // add the tags to the tag ui
                $('#tags').val($(this).attr('tag'));

                // add the description to the ui
                $('#description').val($(this).attr('description'));

                // add the description to the ui
                $('#extended').text($(this).attr('extended'));

                // now enable the delete button in case we want to delete it
                $(delicious.EVENTID).trigger(delicious.events.ENABLEDELETE);

            });
        }
    };

    delicious._request(opts);
};


/*
 * verify that auth credentials are correct
 * uses the delicious 'update' api to verify credentials
 * see http://delicious.com/help/api#posts_update
 *
*/
delicious.authorize = function (options) {
    var defaults, opts;

    defaults = {
        url: "https://api.del.icio.us/v1/posts/update"
    };
    opts = $.extend({}, defaults, options);
    delicious._request(opts);
};


/*
 * recommends tags for a given url
 *
*/
delicious.suggestions = function (url, callback) {
    var opts = {
        url: delicious.api_url + "/posts/get",
        data: {url: url},
        success: function (xml) {
            var suggestions = [];
            $(xml).find("post").map(function () {
                suggestions.push($(this).attr('tags'));
            });
            callback(suggestions.unique());
        }
    };

    delicious._request(opts);
};


// dom hook for triggering/catching events fired
delicious.EVENTID = '#bmarkbody';

/**
 * Define events supported
 * Currently we've got LOAD, SAVED, ERROR, DELETE, UPDATE
 *
 */
delicious.events = {
    'LOAD': 'load',
    'SAVE': 'save',
    'ERROR': 'error',
    'DELETE': 'delete',
    'ENABLEDELETE': 'enabledelete',
    'UPDATE': 'update'
};


/**
 * On Launch, get the info for the current url
 *
 */
var onload = function (ev) {
    chrome.tabs.getSelected(null, function (tab) {
        var url;

        $('#url').val(tab.url);
        $('#description').val(tab.title);
        $('#api_key').val(localStorage['api_key']);

        // see if we have this url already in the bookie system
        url = $('#url').attr('value');
        delicious.getbookmark(url);


    });
};


/**
 * After pressing the save button, go store the new bookmark
 *
 */
var onsave = function (ev) {
    delicious.savebookmark($('form#form').serialize(), {
        beforeSend: function () {
            $('#submit').attr('disabled', 'disabled').text('Saving...');
        },

        complete: function (xml) {
            var result, code;

            result = $(xml).find("result");
            code = result.attr("code");

            if (code == "done") {
                chrome.browserAction.setBadgeText({text:'+'});
                chrome.browserAction.setBadgeBackgroundColor({color:[15, 232, 12, 255]});

                console.log("Bookmark saved to delicious!");
            } else {
                chrome.browserAction.setBadgeText({text: code});
                console.error("Error saving bookmark: " + code);
            }

             var c = chrome;
             setTimeout(function() {
                 c.browserAction.setBadgeText({text:''});
                 window.close();
             }, 2000);
        }
    });

    ev.preventDefault();
};

/**
 * There was an error in the request made
 *
 */
var onerror = function (request, status, err) {
    error_msg = '- ' + request.status.toString();
    chrome.browserAction.setBadgeText({text: error_msg});

    // the default badge color is red so leaving it out
    console.error("Error during request" + status);
    console.info(request.status);
    console.info(err);
};

/**
 * Make the call to remove the bookmark
 *
 */
var ondelete = function (ev) {
    var url = $('#url').attr('value');
    var api_key = $('#api_key').attr('value');
    delicious.removebookmark(url, api_key);
};

/**
 * If this bookmark was found in the system, enable the user to delete it
 *
 */
var enabledelete = function (ev) {
    $('#delete').show();

    // and make sure we bind the delete event
    $(delicious.EVENTID).bind(delicious.events.DELETE, ondelete);
};


delicious.bind_events = function () {
    bkg.console.log('binding events');

    $(delicious.EVENTID).bind(delicious.events.LOAD, onload);
    $(delicious.EVENTID).bind(delicious.events.SAVE, onsave);
    $(delicious.EVENTID).bind(delicious.events.ENABLEDELETE, enabledelete);
    $(delicious.EVENTID).bind(delicious.events.DELETE, ondelete);

    // and we also have to bind the various controls to fire off the events
    // we're catching above
    $('form#form').bind('submit', function (ev) {
        $(delicious.EVENTID).trigger(delicious.events.SAVE);
        ev.preventDefault();
    });

    // bind the delete button
    $('#delete').bind('click', function (ev) {
        $(delicious.EVENTID).trigger(delicious.events.DELETE);
        ev.preventDefault();
    });
};


/**
 * Array.unique( strict ) - Remove duplicate values
 * see http://4umi.com/web/javascript/array.php#unique
 *
*/
Array.prototype.unique = function (b) {
    var a = [], i, l = this.length;
    for (i = 0; i < l; i++) {
        if (a.indexOf(this[i], 0, b) < 0) {
            a.push(this[i]);
        }
    }
    return a;
};
