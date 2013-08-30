YUI().use('bookie-chrome', function (Y) {
    // start out with the suggested tags hidden
    Y.one('#suggested_tags').hide();
    var run = function (tab_data) {
        if (tab_data) {
            var settings = new Y.bookie.OptionsModel();
            // load the settings from the extension for use
            settings.load();

            // don't worry about loading the content of the page if we
            // don't have it set in our options
            if (settings.get('cache_content') !== 'true') {
                // then skip it, we don't want the added load on the
                // browser or the server
            } else {
                chrome.extension.onRequest.addListener(
                    function(request, sender, sendResponse) {
                        if (request.id === 'from_readable') {
                            Y.one('#content').set('value', request.html);
                        }
                    }
                );

                var bkg = chrome.extension.getBackgroundPage();
                bkg.inject_readable(function () {
                    var c = document.getElementById('content');
                    c.value = bkg.get_html_content();
                });
            }

            var bookmark = new Y.bookie.Bmark(Y.merge(
                tab_data, {
                    api_cfg: settings.get_apicfg()
                }
            ));

            var c = new Y.bookie.chrome.Popup({
                settings: settings,
                model: bookmark
            });
            c.render();

        } else {
            var n = new Y.bookie.chrome.Notification({
                code: '9999',
                type: 'error',
                title: 'Err',
                message: 'Could not find a url to bookmark.'
            });
        }
    };

    // this could be fed tab info via the url
    // usually in the case of a keyboard shortcut loading this in a
    // new tab vs the icon popup
    var parts = window.location.hash.substring(1).split('|');
    var tab_data;
    if (parts.length === 2) {
        tab_data = {
            'url': window.atob(parts[0]),
            'description': window.atob(parts[1])
        };
        run(tab_data);
    } else {
        // first get the windowid
        chrome.windows.getCurrent(function(window) {
            // then get the current active tab in that window
            chrome.tabs.query({
                active: true,
                windowId: window.id
            }, function (tabs) {
                // and use that tab to fill in out title and url
                var tab = tabs[0];
                run({
                    url: tab.url,
                    description: tab.title
                });
            });
        });
    }
});
