/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, jQuery: false */

/**
 * THIS IS A LIE
 *
 * I've just copied over the chrome file so I can keep the API bits the same
 * and replace them with the FF specific version of the code.
 *
 * Hopefully, if all goes well this can drop in replace and we can head towards
 * bookie core
 *
 */

// now this will extend the original bookie module with added chrome specific
// functionality
(function (module, $) {
    $b = module;

    // PRIVATE

    /**
     * Implement the settings storage we need
     *
     */
    $b.settings = {
        'init':function () {
            $b.prefs = Components.classes["@mozilla.org/preferences-service;1"]
                .getService(Components.interfaces.nsIPrefService)
                .getBranch("bookie.");
            $b.prefs.QueryInterface(Components.interfaces.nsIPrefBranch2);
            $b.prefs.addObserver("", $b, false);
        },
        'get': function (key) {
            $b.log('GET ' + key);
            return $b.prefs.getCharPref(key);
        },
        'set': function (key) {
            $b.log('not implemented set');
        }
    };


    /**
     * This will call a shared function that maps data to the ui form
     * The specifics here is getting the tab info from Chrome vs FF
     *
     */
    $b.populateForm = function () {
        $b.log('populating form');
        $b.log(window.gBrowser);

        if (window.gBrowser !== undefined) {
            var current_tab, tab_obj;

            currentTab = gBrowser.contentDocument;
            $b.log('current tab');

            tab_obj = {
                'url': currentTab.location.href,
                'title': currentTab.title
            }

            $b.log(tab_obj);
            $b.populateFormBase(tab_obj);

        } else {
            // when running unit tests the firefox stuff isn't available
            // so we have to fake it
            $b.populateFormBase({'url':window.location.href,
                'title': "Testing stuff"
            });
        }
    };


    /**
     * We can't do the focus until after the panel window has loaded
     *
     */
    $b.post_load = function () {
        $('#tags').focus();
    };


    /**
     * Allow for the keyboard action to perform the same thing that clicking
     * the icon will do, basically open the panel and run onload()
     *
     */
    $b.onKeyboardShortcut = function() {
        $('#bookie-panel').get(0).openPopup($('#bookie-button').get(0), 'before_start');
        $b.events.onload();
        $b.post_load();
    };


    $b.ui.notify = function(notification) {
        $b.log('called notify');
        // showBadge(notification);


        // if (window.chrome !== undefined && chrome.tabs) {
        //     if(notification.type === "error") {
        //         webkitNotifications.createNotification(
        //             'delicious.png',
        //             notification.shortText,
        //             notification.longText
        //             ).show();
        //     } else {
        //         window.close();
        //     }
        // }
    };


    function showBadge(notification) {
        $b.log('called show badge');

        // var color,
        //     badge;

        // switch(notification.type) {
        //     case "error":
        //         color = "red";
        //         badge = "Err";
        //         break;
        //     case "info":
        //         color = "green";
        //         badge = "Ok";
        //         break;
        //     default:
        //         console.log("Unknown notification type: " + notification.type);
        // }
        // // add a notice to the badge as necessary
        // $b.ui.badge.set(badge, 5000, $b.ui.badge.colors[color]);
    };

    // provide helpers for dealing with notifications from events fired through
    // the plugin. I think at some point we really want to do something to map
    // these to generic notifications and provide these more as a chrome
    // specific mapper
    // $b.ui.badge = {
    //     'clear': function (millis) {
    //         if (window.chrome !== undefined && chrome.tabs) {
    //             background.ui.badge.clear(millis);
    //         }
    //     },

    //     'set': function (text, milliseconds, bgcolor) {
    //         if (bgcolor) {
    //             if (window.chrome !== undefined && chrome.tabs) {
    //                 chrome.browserAction.setBadgeBackgroundColor({color: bgcolor});
    //             }
    //         }

    //         if (window.chrome !== undefined && chrome.tabs) {
    //             chrome.browserAction.setBadgeText({text: text});
    //         }

    //         if (milliseconds) {
    //             $b.ui.badge.clear(milliseconds);
    //         }
    //     },

    //     // colors must be defined in the RGBA syntax for the chrome api to work
    //     'colors': {
    //         'green': [15, 232, 12, 255],
    //         'red': [200, 50, 50, 255]
    //     }
    // };

    $b.ff_init = function() {
        $b.log('Adding to bookie in bookie-firefox');
        $b.settings.init();
        $b.log($b.settings.get('api_url'));

        $('#bookie-button').attr('oncommand', '$b.onKeyboardShortcut()');
        $('#bookie-button').attr('onpopupshowing', '$b.events.onload()');
        $('#bookie-button').attr('onpopupshown', '$b.post_load()');
        $('#bookie-submit').attr('command', 'bookie-submit-cmd');
    };

    $b.shutdown = function() {
        $b.prefs.removeObserver("", module);
    };

    return $b;

})(bookie || {}, jq_var);
