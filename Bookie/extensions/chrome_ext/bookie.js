/*jslint eqeqeq: false, browser: true, debug: true, onevar: true
, plusplus: false, newcap: false  */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false */

var bookie = {};

// dom hook for triggering/catching events fired
bookie.EVENTID = '#bmarkbody';

/**
 * Define events supported
 * Currently we've got LOAD, SAVED, ERROR, DELETE, UPDATE
 *
 */
bookie.events = {
    'LOAD': 'load',
    'SAVE': 'save',
    'ERROR': 'error',
    'DELETE': 'delete',
    'ENABLEDELETE': 'enabledelete',
    'UPDATE': 'update'
};

/**
 * The server can respond to request with a number of success/error codes. We
 * want to provide a common mapping from application to client side code so
 * that we can provide a decent notification to the user
 *
 */
bookie.response_codes = {
    '200': 'Ok',
    '403': 'NoAuth',

    // some codes from the xml response in the delicious api
    'done': 'Ok'
};


bookie.badge = {
    'clear': function () {
        chrome.browserAction.setBadgeText({text: ''});
    },

    'set': function (text, bgcolor) {
        if (bgcolor !== undefined) {
            chrome.browserAction.setBadgeBackgroundColor({color: bgcolor});
        }

        chrome.browserAction.setBadgeText({text: text});
    },

    'colors': {
        'green': [15, 232, 12, 255]
    }
};
