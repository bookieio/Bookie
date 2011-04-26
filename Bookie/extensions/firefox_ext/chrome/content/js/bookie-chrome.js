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
    // PRIVATE

    // we have no background page, not sure how we're going to do the content
    // fetching yet
    // var background;

    // if (window.chrome !== undefined && chrome.tabs) {
    //     background = chrome.extension.getBackgroundPage();
    // } else {
    //     background = undefined;
    // }

    /**
     * This will call a shared function that maps data to the ui form
     * The specifics here is getting the tab info from Chrome vs FF
     *
     */
    module.populateForm = function () {
        if (window.gBrowser !== undefined) {
            var current_tab, tag_obj;

            currentTab = gBrowser.contentDocument;
            tag_obj = {
                'url': currentTab.location.href,
                'title': currentTab.title
            }

            module.populateFormBase(tag_obj);

        } else {
            // when running unit tests the firefox stuff isn't available
            // so we have to fake it
            module.populateFormBase({'url':window.location.href,
                'title': "Testing stuff"
            });
        }
    };

    module.ui.notify = function(notification) {
        module.consoleService.logStringMessage('called notify');
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
    }

    function showBadge(notification) {
        module.consoleService.logStringMessage('called show badge');
        
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
        // module.ui.badge.set(badge, 5000, module.ui.badge.colors[color]);
    }


    // provide helpers for dealing with notifications from events fired through
    // the plugin. I think at some point we really want to do something to map
    // these to generic notifications and provide these more as a chrome
    // specific mapper
    // module.ui.badge = {
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
    //             module.ui.badge.clear(milliseconds);
    //         }
    //     },

    //     // colors must be defined in the RGBA syntax for the chrome api to work
    //     'colors': {
    //         'green': [15, 232, 12, 255],
    //         'red': [200, 50, 50, 255]
    //     }
    // };

    return module;

})(bookie || {}, jQuery);
