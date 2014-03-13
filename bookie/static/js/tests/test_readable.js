/**
 * Test the readable api helper
 *
 */
YUI.add('bookie-test-readable', function (Y) {
    var ns = Y.namespace('bookie.test.readable');
    ns.suite = new Y.Test.Suite('Account API Tests');

    var gen_fakeio = function (test_function) {
        return function (url, cfg) {
            test_function(url, cfg);
        };
    };

    ns.suite.add(new Y.Test.Case({
        name: "Readable Api Tests",

        setUp: function () {
        },

        testModuleExists: function () {
            Y.Assert.isObject(Y.bookie.readable.Api,
                "Should find an object for readable api module");
        },

        testInitCorrect: function () {
            var test_url = 'http://www.google.com',
                api = new Y.bookie.readable.Api({
                    url: test_url
                });

            Y.Assert.areEqual(test_url, api.get('url'));
            Y.Assert.areEqual(
                'http://r.bmark.us/readable/http%3A//www.google.com',
                api.build_url());
        },

        testLiveApiCall: function () {
            var that = this,
                test_url = 'http://docs.bmark.us/en/latest/index.html',
                api = new Y.bookie.readable.Api({
                    url: test_url
                });

            api.set('sync', true);
            api.call({
                success: function (data, response, args) {
                    var resp_keys = [
                        'content',
                        'content_type',
                        'domain',
                        'headers',
                        'is_error',
                        'request_time',
                        'short_title',
                        'status_code',
                        'status_message',
                        'title',
                        'url'
                    ];
                    Y.ObjectAssert.hasKeys(resp_keys, data);
                },
                error: function (data, status_str, response, args) {}
            });
        }
    }));

}, '0.4', {
    requires: [
        'test', 'bookie-readable'
    ]
});
