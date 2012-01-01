// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-api', function (Y) {
    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    var api_test = new Y.Test.Case({
        name: "API Tests",

        testApiExists: function () {
            Y.Assert.isObject(Y.bookie.Api,
                              "Should find an objcet for Api module");
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
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1'
                },
                api = new Y.bookie.Api.route.BmarksAll(API_CFG);

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
                            Y.Assert.areEqual(
                                'admin',
                                data.bmarks[0].username
                            );
                        });
                    }
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1',
                    username: 'admin',
                    api_key: '2dcf75460cb5'
                },
                api = new Y.bookie.Api.route.UserBmarksAll(API_CFG);

            api.call(callbacks);
            this.wait(1000);
        },

        testTagComplete: function () {
            var that = this,
                callbacks = {
                    success: function (data, request) {
                        that.resume(function () {
                            Y.Assert.areEqual('200', request.status);
                            Y.Assert.areEqual(5, data.tags.length);
                        });
                    }
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1',
                    username: 'admin',
                    api_key: '2dcf75460cb5',
                },
                api = new Y.bookie.Api.route.TagComplete(API_CFG);

            api.call(callbacks, 'boo', '');
            this.wait(1000);
        },

        testGetUserBmark: function () {
            var that = this,
                hash_id = 'b1210b874f52a1',
                callbacks = {
                    success: function (data, request) {
                        that.resume(function () {
                            Y.Assert.areEqual('200', request.status);
                            Y.Assert.isTrue(Y.Lang.isObject(data.bmark));
                            Y.Assert.areEqual(12, data.bmark.bid);
                        });
                    }
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1',
                    hash_id: hash_id,
                    username: 'admin'
                },
                api = new Y.bookie.Api.route.Bmark(API_CFG);

            api.call(callbacks);
            this.wait(1000);
        },

// need a good way to test this out...*sigh*
// it's been tested ok by hand
//         testDeleteBmark: function () {
//             var that = this,
//                 hash_id = '6c4370829d7ebc',
//                 callbacks = {
//                     success: function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     username: 'admin',
//                     api_key: '2dcf75460cb5',
//                     hash_id: hash_id,
//                 },
//                 api = new Y.bookie.Api.route.UserBmarkDelete(API_CFG);
// 
//             api.call(callbacks);
//             this.wait(1000);
//         },

        testApiKey: function () {
            var that = this,
                callbacks = {
                    success: function (data, request) {
                        that.resume(function () {
                            Y.Assert.areEqual('200', request.status);
                            Y.Assert.areEqual(12, data.api_key.length);
                            Y.Assert.areEqual('admin', data.username);
                        });
                    }
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1',
                    username: 'admin',
                    api_key: '2dcf75460cb5',
                },
                api = new Y.bookie.Api.route.UserApiKey(API_CFG);

            api.call(callbacks);
            this.wait(1000);
        },

    });

    Y.Test.Runner.add(api_test);
    Y.Test.Runner.run();
});
