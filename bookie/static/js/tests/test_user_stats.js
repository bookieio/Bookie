// Create a new YUI instance and populate it with the required modules.
YUI.add('bookie-test-userstats', function (Y) {
    var ns = Y.namespace('bookie.test.userstats');
    ns.suite = new Y.Test.Suite('User Stats Tests');

    var json_response = {
        "count": [
	{
            "attrib": "user_bookmarks_admin",
            "data": 10,
            "id": 18,
            "tstamp": "2014-03-04 00:00:00"}
        ],
        "start_date": "2014-03-04 00:00:00",
        "end_date": "2014-03-05 00:00:00"
    };
    ns.suite.add(new Y.Test.Case({
        name: "User Stats Tests",

        setUp: function() {
        },

        testApiExists: function() {
            Y.Assert.isObject(Y.bookie.Api,
                              "Should find an object for Api module");
        },

        testChecking: function() {
            var old_method = Y.bookie.Api.route.UserBmarkCount;
            Y.bookie.Api.route.UserBmarkCount = function(cfg){
                return {
                    call: function(cfg) {
                        cfg.error(null, null, {
                            response: json_response
                        });
                    }
                }
            };
            var API_CFG = {
                url: 'http://127.0.0.1:6543/api/v1',
                username: 'admin',
                api_key: '123456'
	    };
            var user_stats = Y.bookie.Api.route.UserBmarkCount(API_CFG);
            var user_stats = new Y.bookie.UserBmarkCountView({
                api_cfg: API_CFG,
                container: Y.one('body')
            });
            user_stats.render();
        }
        
    }));
}, '0.4', {
    requires: [
        'test', 'bookie-view'
    ]
});
