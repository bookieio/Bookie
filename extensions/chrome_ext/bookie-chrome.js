/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, jQuery: false */

/* chrome-extension-specific bookie functionality */

// now this will extend the original bookie module with added chrome specific
// functionality
(function (module, $) {
    // PRIVATE
    var background;

    if (window.chrome !== undefined && chrome.tabs) {
        background = chrome.extension.getBackgroundPage();
    } else {
        background = undefined;
    }

    $b = module;


    /**
     * Implement the settings storage we need
     *
     */
    $b.settings = {
        'init':function () {
            // using localStorage, we're fine
        },
        'get': function (key) {
            $b.log('GET ' + key);
            return localStorage[key];
        },
        'set': function (key, value) {
            localStorage[key] = value;
        }
    };


    /**
     * This will call a shared function that maps data to the ui form
     * The specifics here is getting the tab info from Chrome vs FF
     *
     */
    $b.populateForm = function () {
        if (window.chrome !== undefined && chrome.tabs) {
            chrome.tabs.getSelected(null, $b.populateFormBase);

            var api_url = $b.settings.get('api_url');
            $('#bookie_site').attr('href', api_url).attr('title', api_url);

        } else {
            // when running unit tests the chrome stuff isn't available
            // so we have to fake it
            $b.populateFormBase({'url':window.location.href,
                'title': "Testing stuff"
            });
        }
    };

    $b.ui.notify = function(notification) {
        showBadge(notification);


        if (window.chrome !== undefined && chrome.tabs) {
            if(notification.type === "error") {
                //show a desktop notification
                var n = webkitNotifications.createNotification(
                    'logo.128.png',
                    notification.shortText,
                    notification.longText
                    );
                n.show();

                //hide the desktop notification after 5 seconds
                window.setTimeout(function() {
                    n.cancel();
                }, 5000);
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
        $b.ui.badge.set(badge, 5000, $b.ui.badge.colors[color]);
    }

    // provide helpers for dealing with notifications from events fired through
    // the plugin. I think at some point we really want to do something to map
    // these to generic notifications and provide these more as a chrome
    // specific mapper
    $b.ui.badge = {
        'clear': function (millis) {
            if (window.chrome !== undefined && chrome.tabs) {
                background.ui.badge.clear(millis);
            }
        },

        'set': function (text, milliseconds, bgcolor) {
            if (bgcolor) {
                if (window.chrome !== undefined && chrome.tabs) {
                    chrome.browserAction.setBadgeBackgroundColor({color: bgcolor});
                }
            }

            if (window.chrome !== undefined && chrome.tabs) {
                chrome.browserAction.setBadgeText({text: text});
            }

            if (milliseconds) {
                $b.ui.badge.clear(milliseconds);
            }
        },

        // colors must be defined in the RGBA syntax for the chrome api to work
        'colors': {
            'green': [15, 232, 12, 255],
            'red': [200, 50, 50, 255]
        }
    };


    $b.chrome_init = function () {
        $b.log($);
        $($b.EVENTID).bind($b.events.LOAD, $b.events.onload);
        $($b.EVENTID).trigger($b.events.LOAD);

    };

    return $b;

})(bookie || {}, jq_var);
