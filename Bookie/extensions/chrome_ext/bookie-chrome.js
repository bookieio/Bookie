/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, jQuery: false */

/* chrome-extension-specific bookie functionality */

// now this will extend the original bookie module with added chrome specific
// functionality
(function (module, $) {
    // PRIVATE
    var background;

    if (chrome && chrome.tabs) {
        background = chrome.extension.getBackgroundPage();
    } else {
        background = undefined;
    }

    /**
     * This will call a shared function that maps data to the ui form
     * The specifics here is getting the tab info from Chrome vs FF
     *
     */
    module.populateForm = function () {
        if (chrome && chrome.tabs) {
            chrome.tabs.getSelected(null, module.populateFormBase);
        } else {
            // when running unit tests the chrome stuff isn't available
            // so we have to fake it
            module.populateFormBase({'url':window.location.href,
                'title': "Testing stuff"
            });
        }
    };

    module.ui.notify = function(notification) {
        showBadge(notification);


        if (chrome && chrome.tabs) {
            if(notification.type === "error") {
                webkitNotifications.createNotification(
                    'delicious.png',
                    notification.shortText,
                    notification.longText
                    ).show();
            } else {
                window.close();
            }
        }
    }

    function showBadge(notification) {
        var color,
            badge;

        switch(notification.type) {
            case "error":
                color = "red";
                badge = "Err";
                break;
            case "info":
                color = "green";
                badge = "Ok";
                break;
            default:
                console.log("Unknown notification type: " + notification.type);
        }
        // add a notice to the badge as necessary
        module.ui.badge.set(badge, 5000, module.ui.badge.colors[color]);
    }

    // provide helpers for dealing with notifications from events fired through
    // the plugin. I think at some point we really want to do something to map
    // these to generic notifications and provide these more as a chrome
    // specific mapper
    module.ui.badge = {
        'clear': function (millis) {
            if (chrome && chrome.tabs) {
                background.ui.badge.clear(millis);
            }
        },

        'set': function (text, milliseconds, bgcolor) {
            if (bgcolor) {
                if (chrome && chrome.tabs) {
                    chrome.browserAction.setBadgeBackgroundColor({color: bgcolor});
                }
            }

            if (chrome && chrome.tabs) {
                chrome.browserAction.setBadgeText({text: text});
            }

            if (milliseconds) {
                module.ui.badge.clear(milliseconds);
            }
        },

        // colors must be defined in the RGBA syntax for the chrome api to work
        'colors': {
            'green': [15, 232, 12, 255],
            'red': [200, 50, 50, 255]
        }
    };

    return module;

})(bookie || {}, jQuery);
