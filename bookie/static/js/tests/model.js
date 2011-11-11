// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-model', function (Y) {
    var A = Y.Assert,
        model_test = new Y.Test.Case({
        name: "Model Tests",

        empty_model: function () {
                return new Y.bookie.Bmark({
                    'bid': "",
                    'hash_id': "",
                    'description': "",
                    'extended': "",
                    'stored': "2011-11-10 20:57:40.273044",
                    'updated': "2011-11-11 20:57:40.273044",
                    'dateinfo': "",
                    'prettystored': ""
                });
        },

        test_model: function () {
                return new Y.bookie.Bmark({
                    'bid': 1,
                    'hash_id': "testhash",
                    'description': "description",
                    'extended': "longer description",
                    'stored': "2011-11-10 20:57:40.273044",
                    'updated': "2011-11-11 20:57:40.273044",
                    'dateinfo': "",
                    'prettystored': ""
                });
        },

        testBmarkExists: function () {
            A.isObject(Y.bookie.Bmark,
                              "Should find an objcet for Bmark model");
        },

        testBmarkProperties: function () {
            var prop_list = ['bid', 'hash_id', 'description', 'extended'],
                prop_dates = {
                    stored: String(new Date("2011-11-10 20:57:40.273044")),
                    updated: String(new Date("2011-11-11 20:57:40.273044")),
                    dateinfo: "11/10",
                    prettystored: "11/10/2011 20:57"
                },
                bmark = this.empty_model();

            Y.each(prop_list, function (prop) {
                // check that this property exists
                A.areEqual("", bmark.get(prop));
            });

            Y.Object.each(prop_dates, function (value, prop) {
                // check that this property exists
                A.areEqual(value, String(bmark.get(prop)));
            });

            A.areEqual(undefined, bmark.get('not_exist'));
        },

        testDateGetters: function () {
            var bmark = this.test_model();

            A.isInstanceOf(Date, bmark.get('stored'),
                "Stored should be converted from string to Date object");
        },



    });

    Y.Test.Runner.add(model_test);

    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    Y.Test.Runner.run();
});
