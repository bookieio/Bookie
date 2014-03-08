// Create a new YUI instance and populate it with the required modules.
YUI.add('bookie-test-userstats', function (Y) {
    var ns = Y.namespace('bookie.test.userstats');
    ns.suite = new Y.Test.Suite('User Stats Tests');

    ns.suite.add(new Y.Test.Case({
        name: "User Stats Tests",

    }));
}, '0.4', {
    requires: [
        'test', 'bookie-view'
    ]
});
