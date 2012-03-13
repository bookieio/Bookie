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

    gen_fakeio = function (test_function) {
        var fake_io = function (url, cfg) {
            test_function(url, cfg);
        }
        return fake_io;
    };

    var api_test = new Y.Test.Case({
        name: "API Tests",


        setUp: function () {
        },

        testApiExists: function () {
            Y.Assert.isObject(Y.bookie.Api,
                              "Should find an objcet for Api module");
        },

        testPublicBmarkList: function () {
            var that = this,
                hit = false,
                test_func = function (url, cfg) {
                    Y.Assert.areEqual('GET', cfg.method);
                    Y.Assert.areEqual('http://127.0.0.1:6543/api/v1/bmarks/',
                        url);
                    Y.ObjectAssert.areEqual({
                        count: 10,
                        page: 0,
                        resource: undefined,
                        username: "",
                        with_content: false
                    }, cfg.data);
                    hit = true;
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1'
                },
                api = new Y.bookie.Api.route.BmarksAll(API_CFG);

            Y.io = gen_fakeio(test_func);
            api.call({});
            Y.Assert.isTrue(hit);
        },

        testPublicSearch: function () {
            var that = this,
                hit = false,
                test_func = function (url, cfg) {
                    Y.Assert.areEqual('GET', cfg.method);
                    Y.Assert.areEqual(
                        'http://127.0.0.1:6543/api/v1/bmarks/search/',
                        url);
                    Y.ObjectAssert.areEqual({
                        count: 10,
                        page: 0,
                        resource: undefined,
                        username: "",
                        with_content: true
                    }, cfg.data);
                    hit = true;
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1'
                },
                api = new Y.bookie.Api.route.Search(API_CFG);

            Y.io = gen_fakeio(test_func);
            api.call({});
            Y.Assert.isTrue(hit);
        },

        testPublicSearchTerms: function () {
            var that = this,
                hit = false,
                test_func = function (url, cfg) {
                    Y.Assert.areEqual('GET', cfg.method);
                    Y.Assert.areEqual(
                        'http://127.0.0.1:6543/api/v1/bmarks/search/books',
                        url);
                    Y.ObjectAssert.areEqual({
                        count: 10,
                        page: 0,
                        resource: undefined,
                        username: "",
                        with_content: true
                    }, cfg.data);
                    hit = true;
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1'
                },
                api = new Y.bookie.Api.route.Search(Y.merge(API_CFG, {
                    phrase: ['books']
                }));

            Y.io = gen_fakeio(test_func);
            api.call({});
            Y.Assert.isTrue(hit);
        },

        testUserPublicSearchTerms: function () {
            var that = this,
                hit = false,
                test_func = function (url, cfg) {
                    Y.Assert.areEqual('GET', cfg.method);
                    Y.Assert.areEqual(
                        'http://127.0.0.1:6543/api/v1/admin/bmarks/search/books',
                        url);
                    Y.ObjectAssert.areEqual({
                        count: 10,
                        page: 0,
                        resource: undefined,
                        username: "admin",
                        with_content: true
                    }, cfg.data);
                    hit = true;
                },
                API_CFG = {
                    url: 'http://127.0.0.1:6543/api/v1'
                },
                api = new Y.bookie.Api.route.UserSearch(Y.merge(API_CFG, {
                    phrase: ['books'],
                    username: 'admin'
                }));

            Y.io = gen_fakeio(test_func);
            api.call({});
            Y.Assert.isTrue(hit);
        },

//         testFilteredPublicBmarkList: function () {
//             var that = this,
//                 tag = 'books',
//                 callbacks = {
//                     'success': function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.areEqual(10, data.count);
//
//                             Y.Array.each(data.bmarks, function (n) {
//                                 Y.Assert.areNotEqual(-1, n.tag_str.indexOf(tag));
//                             });
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     tags: [tag]
//                 },
//                 api = new Y.bookie.Api.route.BmarksAll(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         },
//
//         testUserBmarkList: function () {
//             var that = this,
//                 callbacks = {
//                     'success': function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.areEqual(10, data.count);
//                             Y.Assert.areEqual(
//                                 'admin',
//                                 data.bmarks[0].username
//                             );
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     username: 'admin',
//                     resource: 'admin',
//                     api_key: '2dcf75460cb5'
//                 },
//                 api = new Y.bookie.Api.route.UserBmarksAll(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         },
//
//         testTagComplete: function () {
//             var that = this,
//                 callbacks = {
//                     success: function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.areEqual(5, data.tags.length);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     username: 'admin',
//                     api_key: '2dcf75460cb5'
//                 },
//                 api = new Y.bookie.Api.route.TagComplete(API_CFG);
//
//             api.call(callbacks, 'boo', '');
//             this.wait(1000);
//         },
//
//         testGetUserBmark: function () {
//             var that = this,
//                 hash_id = 'b1210b874f52a1',
//                 callbacks = {
//                     success: function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.isTrue(Y.Lang.isObject(data.bmark));
//                             Y.Assert.areEqual(12, data.bmark.bid);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     hash_id: hash_id,
//                     username: 'admin'
//                 },
//                 api = new Y.bookie.Api.route.Bmark(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         },
//
// // need a good way to test this out...*sigh*
// // it's been tested ok by hand
// //         testDeleteBmark: function () {
// //             var that = this,
// //                 hash_id = '6c4370829d7ebc',
// //                 callbacks = {
// //                     success: function (data, request) {
// //                         that.resume(function () {
// //                             Y.Assert.areEqual('200', request.status);
// //                         });
// //                     }
// //                 },
// //                 API_CFG = {
// //                     url: 'http://127.0.0.1:6543/api/v1',
// //                     username: 'admin',
// //                     api_key: '2dcf75460cb5',
// //                     hash_id: hash_id,
// //                 },
// //                 api = new Y.bookie.Api.route.UserBmarkDelete(API_CFG);
// //
// //             api.call(callbacks);
// //             this.wait(1000);
// //         },
//
//         testApiKey: function () {
//             var that = this,
//                 callbacks = {
//                     success: function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.areEqual(12, data.api_key.length);
//                             Y.Assert.areEqual('admin', data.username);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     username: 'admin',
//                     api_key: '7745ac02c6dc'
//                 },
//                 api = new Y.bookie.Api.route.UserApiKey(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         },
//
//         testApiPing: function () {
//             var that = this,
//                 callbacks = {
//                     success: function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.areEqual(true, data.success);
//                             Y.Assert.areEqual("Looks good", data.message);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     username: 'admin',
//                     api_key: '7745ac02c6dc'
//                 },
//                 api = new Y.bookie.Api.route.Ping(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         },
//
//         testApiPingFailsMissingv1: function () {
//             var that = this,
//                 callbacks = {
//                     success: function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.areEqual(false, data.success);
//                             Y.Assert.areEqual("The API url should be /api/v1", data.message);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/',
//                     username: 'admin',
//                     api_key: '7745ac02c6dc'
//                 },
//                 api = new Y.bookie.Api.route.Ping(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         },
//
//         testApiPingFailsNoAuth: function () {
//             var that = this,
//                 callbacks = {
//                     success: function (data, request) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('200', request.status);
//                             Y.Assert.areEqual(false, data.success);
//                             Y.Assert.areEqual("Missing username in your api url.", data.message);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     api_key: '7745ac02c6dc'
//                 },
//                 api = new Y.bookie.Api.route.Ping(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         },
//
//         testApiPingFailsBadAuth: function () {
//             var that = this,
//                 callbacks = {
//                     success: function (data, request) {
//                         console.log('should not be success, but 403');
//                     },
//                     error: function (data, status_str, response, args) {
//                         that.resume(function () {
//                             Y.Assert.areEqual('Not authorized for request.',
//                                 data.error);
//                             Y.Assert.areEqual('Forbidden', status_str);
//                         });
//                     }
//                 },
//                 API_CFG = {
//                     url: 'http://127.0.0.1:6543/api/v1',
//                     username: 'admin',
//                     api_key: 'badauthkey'
//                 },
//                 api = new Y.bookie.Api.route.Ping(API_CFG);
//
//             api.call(callbacks);
//             this.wait(1000);
//         }
    });

    Y.Test.Runner.add(api_test);
    Y.Test.Runner.run();
});
