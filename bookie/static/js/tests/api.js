// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-api', function (Y) {
    var api_test = new Y.Test.Case({
        name: "API Tests",

        /**
         * Just provide a default test api instance
         *
         */
        get_api: function () {
            return api = new Y.bookie.Api({
                       'url': 'http://127.0.0.1:6543',
                       'username': 'admin',
                       'api_key': '2dcf75460cb5'
                   });
        },

        testApiExists: function () {
            Y.Assert.isObject(Y.bookie.Api,
                              "Should find an objcet for Api module");
        },

        testMissingRoute: function () {
            var hit = false;
            try {
                var api = new Y.bookie.Api();
            } catch(err) {
                hit = true
            }

            Y.Assert.isTrue(hit);
        },

        testDefaultParams: function () {
            var api = new Y.bookie.Api({'route': 'bmarks_all'});

            Y.Assert.areEqual("", api.get('url'));
            Y.Assert.areEqual("", api.get('username'));
            Y.Assert.areEqual("", api.get('api_key'));
        },

        testInitWithParams: function () {
            var api = new Y.bookie.Api({
                'route': 'bmarks_all',
                'url': 'https://bmark.us',
                'username': 'admin',
                'api_key': '123456'
            });

            Y.Assert.areEqual("https://bmark.us", api.get('url'));
            Y.Assert.areEqual("admin", api.get('username'));
            Y.Assert.areEqual("123456", api.get('api_key'));
        },

        testPublicBmarkList: function () {
            var that = this,
                callbacks = {
                    'success': function (data, request) {
                                that.resume(function () {
                                    Y.Assert.areEqual('200', request.status);
                                    Y.Assert.areEqual(10, data.count);
                                });
                           }
                },
                api = new Y.bookie.Api({
                      'route': 'bmarks_all',
                      'url': 'http://192.168.0.246:6543/api/v1',
                      'username': 'admin',
                      'api_key': '2dcf75460cb5'
                });

            api.call(callbacks);
            this.wait(1000);
        },

        testUserBmarkList: function () {
            var that = this,
                callbacks = {
                    'success': function (data, request) {
                                that.resume(function () {
                                    Y.Assert.areEqual('200', request.status);
                                    Y.Assert.areEqual(10, data.count);
                                    Y.Assert.areEqual('admin', data.bmarks[0].username);
                                });
                           }
                },
                api = new Y.bookie.Api({
                      'route': 'bmarks_user',
                      'url': 'http://192.168.0.246:6543/api/v1',
                      'username': 'admin',
                      'options': {
                          'data': {
                              'api_key': '2dcf75460cb5'
                          }
                      }
                });

            api.call(callbacks);
            this.wait(1000);
        },

    });

    Y.Test.Runner.add(api_test);

    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    Y.Test.Runner.run();
});
