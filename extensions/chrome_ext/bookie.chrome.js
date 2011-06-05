/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, jQuery: false */

/* chrome-extension-specific bookie functionality */

// now this will extend the original bookie module with added chrome specific
// functionality
(function (opts) {
    var $b = opts.bookie,
        $ = opts.jquery;

    // PRIVATE
    var background;

    if (window.chrome !== undefined && chrome.tabs) {
        background = chrome.extension.getBackgroundPage();
    } else {
        background = undefined;
    }

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
            return localStorage.getItem(key);
        },
        'set': function (key, value) {
            localStorage.setItem(key, value);
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
                // some post notify checks
                if (notification.longText === "saved") {
                    chrome.tabs.getSelected(null, function (tab) {
                        // we need to hash this into storage
                        var hash_id = bookie.utils.hash_url(tab.url);
                        console.log(hash_id);
                        $b.settings.set(hash_id, true);
                    });
                }
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
        'clear': function(millis) {
            var ttl = millis || 0;
            if (window.chrome !== undefined && chrome.tabs) {
                window.setTimeout(function() {
                    chrome.browserAction.setBadgeText({text: ''});
                }, ttl);
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
            'red': [200, 50, 50, 255],
            'blue': [0, 191, 255, 255]
        }
    };


    $b.chrome_init = function () {
        $b.log($);
        $($b.EVENTID).bind($b.events.LOAD, $b.events.onload);
        $($b.EVENTID).trigger($b.events.LOAD);

    };


    $b.background_init = function () {
        function check_url_bookmarked(url) {
            var is_bookmarked = bookie.utils.is_bookmarked(url);

            // check if we have this bookmarked
            // if so update the badge text with +
            if (is_bookmarked) {
                $b.ui.badge.set('+', false, $b.ui.badge.colors.blue);
            } else {
                console.log('running badge clear');
                $b.ui.badge.clear();

            }
        };

        // bind to the events to check if the current url is bookmarked or not
        chrome.tabs.onUpdated.addListener(
            function(tabId, changeInfo, tab) {
                var tid = tabId;

                // we only want to grab this if we change the current url in
                // the current tab
                if ('url' in changeInfo) {
                    if (tab.url) {
                        chrome.tabs.getSelected(undefined, function (tab) {
                            if (tid === tab.id) {
                                check_url_bookmarked(tab.url);
                            }
                        });
                    } else {
                        console.log('no hash for you');
                    }
                }
            }
        );

        chrome.tabs.onSelectionChanged.addListener(
            function(tabId, changeInfo) {
                chrome.tabs.get(tabId, function (tab) {
                    if (tab.url) {
                        check_url_bookmarked(tab.url);
                    } else {
                        console.log('no hash for you');
                    }
                });
            }
        );

        // add some right-click content menu love for a quick "read later"
        var read_later = function (info, tab) {
            console.log(info);
            console.log(tab);

            if (bookie.settings.get('cache_content') == 'true') {
                // grab the html content of the page to send along for the ride
                bookie.call.read_later(tab.url,
                                       tab.title,
                                       $('#html_content').val());
            } else {
                bookie.call.read_later(tab.url, tab.title);
            }
        };

        chrome.contextMenus.create({"title": "Read Later",
                                    "contexts":["page"],
                                    "onclick": read_later
                                  });

        // test out listening for a call from the content script
        // readable.js for the content of the page to send along in a
        // submission as the content
        chrome.extension.onRequest.addListener(
            function(request, sender, sendResponse) {
                if (request.html) {
                    $('#html_content').val(request.html);
                    console.log('should have content stored');
                } else {
                    console.log('hit the else');
                }
            }
        );

        function get_html_content() {
            return $('#html_content').val();
        };

    }

    return $b;

})(bookie_opts);
