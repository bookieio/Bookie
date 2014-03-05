// Create a new YUI instance and populate it with the required modules.
YUI.add('bookie-test-history', function (Y) {
    var ns = Y.namespace('bookie.test.history');
    ns.suite = new Y.Test.Suite('History Tests');

    ns.suite.add(new Y.Test.Case({
        name: "History Tests",

        testHistoryExists: function () {
            Y.Assert.isObject(Y.bookie.BmarkListHistory,
                              "Should find an object for History module");
        }
    }));
}, '0.4', {
    requires: [
        'test', 'bookie-history-module'
    ]
});
