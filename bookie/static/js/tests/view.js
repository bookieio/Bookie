// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-view', 'bookie-model', function (Y) {
    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    var view_test = new Y.Test.Case({
        name: "View Tests",
        setUp: function () {
            this.model = new Y.bookie.Bmark({
                id: 11,
                hash_id: '123456'
            });
        },

        tearDown: function () {
            Y.one('.view').setContent('');
            delete this.model;
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.BmarkView,
                              "Should find an objcet for Bmark view");
        },

        test_render_view: function () {
            var testview = new Y.bookie.BmarkView({model: this.model});

            testview.render(Y.one('.view'));

            Y.Assert.areEqual(
                Y.one('.view').get('innerHTML'),
                '11',
                'The 11 should be on the view container'
            );
        }
    });

    Y.Test.Runner.add(view_test);
    Y.Test.Runner.run();
});
