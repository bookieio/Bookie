// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-history-module', function (Y) {
    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    var test = new Y.Test.Case({
        name: "History Tests",

        testHistoryExists: function () {
            Y.Assert.isObject(Y.bookie.BmarkListHistory,
                              "Should find an objcet for History module");
        },
    });

    Y.Test.Runner.add(test);
    Y.Test.Runner.run();
});
