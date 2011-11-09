// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-api', function (Y) {
    var api_test = new Y.Test.Case({
        name: "API Tests",

        testApiExists: function () {
            Y.Assert.isObject(Y.bookie.Api);
        },

        testDefaultParams: function () {
            var api = new Y.bookie.Api();

            Y.Assert.areEqual("", api.get('url'));
            Y.Assert.areEqual("", api.get('username'));
            Y.Assert.areEqual("", api.get('api_key'));
        },

        testInitWithParams: function () {
            var api = new Y.bookie.Api({
                'url': 'https://bmark.us',
                'username': 'admin',
                'api_key': '123456'
            });

            Y.Assert.areEqual("https://bmark.us", api.get('url'));
            Y.Assert.areEqual("admin", api.get('username'));
            Y.Assert.areEqual("123456", api.get('api_key'));
        },

        testRecent: function () {
             var api = new Y.bookie.Api({
                    'url': 'http://127.0.0.1:6543',
                    'username': 'admin',
                    'api_key': '2dcf75460cb5'
                }),
                callbacks = {
                    success: function (data, request) {
                        Y.Assert.areEqual('200', request.status);
                        Y.Assert.areEqual(0, data.count);
                    }
                };

            this.wait(function () {
                api.recent({}, callbacks);
            }, 1000);
        }
    });

    Y.Test.Runner.add(api_test);

    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    Y.Test.Runner.run();
});
