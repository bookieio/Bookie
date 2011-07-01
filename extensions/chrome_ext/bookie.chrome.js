/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, jQuery: false */

/* chrome-extension-specific bookie functionality */

// now this will extend the original bookie module with added chrome specific
// functionality
(function (opts) {
    var $b = opts.bookie,
        $ = opts.jquery,
        background;

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
    $b.populateForm = function (tab_obj) {
        if (window.chrome !== undefined && chrome.tabs) {

            if (tab_obj !== undefined) {
                $b.populateFormBase({'url': tab_obj.url,
                                     'title': tab_obj.title},
                                     'chrome_ext');
            } else {
                chrome.tabs.getSelected(null, $b.populateFormBase);
            }

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
                        $b.settings.set(hash_id, true);
                    });

                    window.close();
                }

                // if

            }
        }

    };

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


    /**
     * Copy any tags we have from the last run into our tags ui
     *
     */
    $b.ui.dupe_tags = function (node) {
        var current = $('#tags').val().trim();
        if (current.length > 0) {
            current = current + " ";
        }

        $('#tags').val(current + node.html().trim());
        $('#tags').change();
        node.remove();

        // if we've added all the tags and there are none left, then just hide
        // that div
        if ($("#latest_tags a").length === 0) {
            $('#latest_tags').hide();
        }
    };


    $b.chrome_init = function (current_tab_info) {
        $($b.EVENTID).bind($b.events.LOAD, $b.events.onload);
        $($b.EVENTID).bind($b.events.DUPE_TAGS, $b.ui.dupe_tags);

        $('#latest_tags').delegate('a', 'click', function (ev) {
            ev.preventDefault();
            $b.ui.dupe_tags($(this));
        });

        $($b.EVENTID).trigger($b.events.LOAD, current_tab_info);
    };

    $b.check_url_bookmarked = function(url) {
        var is_bookmarked = $b.utils.is_bookmarked(url);
        console.log('Checking ' + url + ' is bookmarked: ' + is_bookmarked);

        // check if we have this bookmarked
        // if so update the badge text with +
        if (is_bookmarked) {
            $b.ui.badge.set('+', false, $b.ui.badge.colors.blue);
        } else {
            $b.ui.badge.clear();

        }
    }

    $b.background_init = function () {
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
                                $b.check_url_bookmarked(tab.url);
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
                        $b.check_url_bookmarked(tab.url);
                    } else {
                        console.log('no hash for you');
                    }
                });
            }
        );

        // add some right-click content menu love for a quick "read later"
        var read_later = function (info, tab) {
            bookie.api.init(bookie.settings.get('api_url'));
            if (bookie.settings.get('cache_content') === 'true') {
                inject_readable(function () {
                    // grab the html content of the page to send along for the ride
                    bookie.call.read_later(tab.url,
                                       tab.title,
                                       get_html_content());

                });
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

        chrome.extension.onRequest.addListener(
            function(request, sender, sendResponse) {
                if (request.url) {
                    chrome.tabs.getSelected(null, function(tab_obj) {
                        var encoded_url = window.btoa(tab_obj.url),
                            encoded_title = window.btoa(tab_obj.title)
                            hash = [encoded_url, encoded_title].join('|');

                        chrome.tabs.create({url: "popup.html#" + hash});
                    });
                }
            }
        );
    };


    $b.options = {
        'init': function () {
            // populate default field values
            $('#api_key').val(localStorage['api_key']);
            $('#api_url').val(localStorage['api_url']);

            if (localStorage['cache_content'] != 'false') {
                $('#cache_content').attr('checked', 'checked');
            } else {
                $('#cache_content').removeAttr('checked');
            }

            // close window on cancel
            $("#cancelBtn").click(function() { window.close(); });

            // save new values on submit
            $("#form").submit(function(e) {
                localStorage['api_key'] = $('#api_key').val();
                localStorage['api_url'] = $('#api_url').val();

                // do you want us to store the cached content of the
                // current page?
                var cache = $("#cache_content:checked").length;
                if (cache == 1) {
                    localStorage['cache_content'] = true;
                } else {
                    localStorage['cache_content'] = false;
                };

                // notify of successful save
                $('#info').text("Saved").slideDown().delay(3000).slideUp();

                e.preventDefault();
            });

            $("#syncBtn").bind('click', bookie.options.sync);
            $('#circle').hide();
        },

        'sync': function () {
            $('#circle').show();

            // the user might have just added the api and hit save
            // so make sure we reload that info
            $b.api.init($b.settings.get('api_url'));
            $b.api.sync($b.settings.get('api_key'), {
                success: function (data) {
                    var bkg, hash_id;
                    bkg = chrome.extension.getBackgroundPage();
                    for (idx in data.payload.hash_list) {
                        hash_id = data.payload.hash_list[idx];
                        localStorage.setItem(hash_id, true);
                    }

                    $('#circle').hide();
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    console.log(thrownError);
                    console.log(xhr);

                    $b.ui.notify(new $b.Notification('error', 0, 'Error Syncing', 'Check your Bookie URL has been set properly'));
                    $('#circle').hide();
                }
            });
        } // end sync

    };

    return $b;

})(bookie_opts);
