// Create a new YUI instance and populate it with the required modules.
YUI.add('bookie-test-userstats', function (Y) {
    var ns = Y.namespace('bookie.test.userstats');
    ns.suite = new Y.Test.Suite('User Stats Tests');

    ns.suite.add(new Y.Test.Case({
        name: "User Stats Tests",

        setUp: function() {
        },

        tearDown: function() {
        },

        testApiExists: function() {
            Y.Assert.isObject(Y.bookie.Api,
                              "Should find an object for Api module");
        },

        test_error: function() {
            // Stub out the API call with a fake response.
            var old_method = Y.bookie.Api.route.UserBmarkCount;
            Y.bookie.Api.route.UserBmarkCount = function(cfg) {
                return {
                    call: function(cfg) {
                        cfg.error();
                    }
                };
            };
            var user_stats_error = new Y.bookie.UserBmarkCountView();
            user_stats_error.render();
            // The error message should be shown to the user.
            this.wait(function() {
                var error_msg = Y.one('#userstats_msg');
                Y.Assert.areEqual('Error fetching the bookmark count', error_msg.getContent());
                Y.bookie.Api.route.UserBmarkCount = old_method;
            }, 500);
        },

        test_success: function() {
            // Fake bookmark count response.
            var resp = [
            {
                "tstamp": "2014-03-04 00:00:00",
                "data": 20},
            {
                "tstamp": "2014-03-05 00:00:00",
                "data": 25},
            {
                "tstamp": "2014-03-06 00:00:00",
                "data": 22}
            ];
            // Stub out the API call with a fake response.
            var old_method = Y.bookie.Api.route.UserBmarkCount;
            Y.bookie.Api.route.UserBmarkCount = function(cfg) {
                return {
                    call: function(cfg) {
                        cfg.success({
                            count: resp
                        });
                    }
                };
            };
            var user_stats_success = new Y.bookie.UserBmarkCountView();
            user_stats_success.render();
            // No error should be shown in case of a successful response.
            this.wait(function() {
                var success_msg = Y.one('#userstats_msg');
                Y.Assert.areEqual('', success_msg.getContent());
                Y.bookie.Api.route.UserBmarkCount = old_method;
            }, 500);
        }

    }));
}, '0.4', {
    requires: [
        'test', 'bookie-view'
    ]
});
