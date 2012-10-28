YUI.add('bookie-test-rsswatch', function (Y) {
    var ns = Y.namespace('bookie.test.rsswatch'),
        A = Y.Assert;

    ns.suite = new Y.Test.Suite('RSS Watch Tests');

    ns.suite.add(new Y.Test.Case({
        name: "Init Tests",

        setUp: function () {
            var link_html = [
                '<link id="rss_url" href="https://bmark.us/rss" ',
                    'rel="alternate" title="Bookmarks" ',
                    'type="application/rss+xml" />',
            ].join('');

            Y.one('#container').setHTML(link_html);
        },

        tearDown: function () {
            Y.one('#container').setContent('');
        },

        test_module_exists: function () {
            Y.Assert.isObject(Y.bookie.rsswatch.Updater,
                              "Should find an Updater for rsswatch");
        },

        test_loads_default_node: function () {
            var w = new Y.bookie.rsswatch.Updater(),
                n = Y.one('#rss_url');
            Y.Assert.areEqual(n, w.get('rss_node'));
        },

        test_catches_update_event: function () {
            // Verify that we can fire the update event on the instance of the
            // rss watcher.
            var w = new Y.bookie.rsswatch.Updater(),
                n = Y.one('#rss_url');

            w.fire('update', {
                data_url: 'http://bmark.us/api/v1/bmarks/'
            });

            Y.Assert.areEqual(
                n.getAttribute('href'),
                'http://bmark.us/rss/');
        }
    }));

}, '0.4', {
    requires: [
        'test', 'node-event-simulate', 'bookie-rsswatch'
    ]
});
