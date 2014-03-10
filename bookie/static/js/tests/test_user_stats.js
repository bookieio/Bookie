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

        test_error_message: function() {
            var userstats_msg = Y.one('#userstats_msg');
            var API_CFG = {
                url: 'http://127.0.0.1:6543/api/v1',
                username: 'admin',
                api_key: '123456'
	    };
            var user_stats = new Y.bookie.UserBmarkCountView({
                api_cfg: API_CFG,
                container: Y.one('body')
            });
            user_stats.render();
            // During a successful api call, there should be no error message.
            Y.Assert.areEqual('', userstats_msg.getContent());
            var API_CFG_ERROR = {
                url: 'http://127.0.0.1:6543/api/invalidurl',
                username: 'admin',
                api_key: '123456'
            };
            var user_stats_error = new Y.bookie.UserBmarkCountView({
                api_cfg: API_CFG_ERROR,
                container: Y.one('body')
            });
            user_stats_error.render();
            // We need to wait a while to get the response.
            this.wait(function() {
                // During an unsuccessful api call, there should be an error message.
                Y.Assert.areEqual('Error fetching the bookmark count', userstats_msg.getContent());
            }, 500);
        }
        
    }));
}, '0.4', {
    requires: [
        'test', 'bookie-view'
    ]
});
