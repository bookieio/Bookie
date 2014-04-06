// Create a new YUI instance and populate it with the required modules.
YUI.add('bookie-test-stats', function (Y) {
    var ns = Y.namespace('bookie.test.stats');
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

        testUserStatsError: function() {
            // Stub out the API call with a fake response.
            var old_method = Y.bookie.Api.route.UserStats;
            Y.bookie.Api.route.UserStats = function(cfg) {
                return {
                    call: function(cfg) {
                        cfg.error();
                    }
                };
            };
            var user_stats_error = new Y.bookie.UserStatsView();
            user_stats_error.render();
            // The error message should be shown to the user.
            this.wait(function() {
                var error_msg = Y.one('#user_stats_msg');
                Y.Assert.areEqual('Error fetching stats', error_msg.getContent());
                Y.bookie.Api.route.UserStats = old_method;
            }, 500);
        },

        testBookmarkStatsError: function() {
            // Stub out the API call with a fake response.
            var old_method = Y.bookie.Api.route.BookmarkStats;
            Y.bookie.Api.route.UserStats = function(cfg) {
                return {
                    call: function(cfg) {
                        cfg.error();
                    }
                };
            };
            var bookmark_stats_error = new Y.bookie.BookmarkStatsView();
            bookmark_stats_error.render();
            // The error message should be shown to the user.
            this.wait(function() {
                var error_msg = Y.one('#bookmark_stats_msg');
                Y.Assert.areEqual('Error fetching stats', error_msg.getContent());
                Y.bookie.Api.route.BookmarkStats = old_method;
            }, 500);
        },

        testUserStatsSuccess: function() {
            // Fake user stats response.
            var count = 10,
                activations = 20,
                with_bookmarks = 30;
            // Stub out the API call with a fake response.
            var old_method = Y.bookie.Api.route.UserStats;
            Y.bookie.Api.route.UserStats = function(cfg) {
                return {
                    call: function(cfg) {
                        cfg.success({
                            count: count,
                            activations: activations,
                            with_bookmarks: with_bookmarks
                        });
                    }
                };
            };
            var user_stats_success = new Y.bookie.UserStatsView();
            user_stats_success.render();
            // No error should be shown in case of a successful response.
            this.wait(function() {
                var success_msg = Y.one('#user_stats_msg'),
                    stats_count = Y.one('#user_stats_count'),
                    stats_activations = Y.one('#user_stats_activations'),
                    stats_with_bookmarks = Y.one('#user_stats_with_bookmarks');
                Y.Assert.areEqual('', success_msg.getContent());
                Y.Assert.areEqual(count, stats_count.getContent());
                Y.Assert.areEqual(activations, stats_activations.getContent());
                Y.Assert.areEqual(with_bookmarks, stats_with_bookmarks.getContent());
                Y.bookie.Api.route.UserStats = old_method;
            }, 500);
        },

        testBookmarkStatsSuccess: function() {
            // Fake user stats response.
            var count = 10,
                unique_count = 20;
            // Stub out the API call with a fake response.
            var old_method = Y.bookie.Api.route.BookmarkStats;
            Y.bookie.Api.route.BookmarkStats = function(cfg) {
                return {
                    call: function(cfg) {
                        cfg.success({
                            count: count,
                            unique_count: unique_count
                        });
                    }
                };
            };
            var bookmark_stats_success = new Y.bookie.BookmarkStatsView();
            bookmark_stats_success.render();
            // No error should be shown in case of a successful response.
            this.wait(function() {
                var success_msg = Y.one('#bookmark_stats_msg'),
                    stats_count = Y.one('#bookmark_stats_count'),
                    stats_unique_count = Y.one('#bookmark_stats_unique_count');
                Y.Assert.areEqual('', success_msg.getContent());
                Y.Assert.areEqual(count, stats_count.getContent());
                Y.Assert.areEqual(unique_count, stats_unique_count.getContent());
                Y.bookie.Api.route.BookmarkStats = old_method;
            }, 500);
        }
    }));
}, '0.4', {
    requires: [
        'test', 'bookie-view'
    ]
});
