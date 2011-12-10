// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-model', function (Y) {
    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

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
                    'prettystored': "",
                    'uesrname': ""
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

            "Bmark model should exist": function () {
                A.isObject(
                    Y.bookie.Bmark,
                    "Should find an objcet for Bmark model"
                );
            },

            "Bmark model should take a bunch of properties": function () {
                var prop_list = ['bid', 'hash_id', 'description', 'extended'],
                    prop_dates = {
                        stored: String(
                            new Date("2011-11-10 20:57:40.273044")
                        ),
                        updated: String(
                            new Date("2011-11-11 20:57:40.273044")
                        ),
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

            "model date getters should format correctly": function () {
                var bmark = this.test_model();

                A.isInstanceOf(Date, bmark.get('stored'),
                    "Stored should be converted from string to Date object");
            },

            "calling remove should run destroy": function () {
                var bmark = this.test_model();

                // override the destroy method to make sure it gets called
                // right
                bmark.destroy = function (opts, callback) {
                    hit = true;
                    A.isTrue(opts.delete, "Delete should be true in the options");
                }

                bmark.remove();

                A.isTrue(hit, "We should have hit the destroy function");
            },

            "calling remove should fire sync with delete action": function () {
                var bmark = this.test_model();

                // override the sync method to make sure it gets called
                // right
                bmark.sync = function (action, opts, callback) {
                    hit = true;
                    A.areEqual(action, 'delete', 'Delete should be true in the options');
                }

                bmark.remove();
                A.isTrue(hit, "We should have hit the sync with delete");
            }

        }),

        modellist_test = new Y.Test.Case({
            name: "Model Tests",
            test_init: function () {
                var json_bmarks = [
                    model_test.test_model(),
                    model_test.test_model(),
                    model_test.test_model(),
                ]

                var bmarks = new Y.bookie.BmarkList();
                bmarks.add(json_bmarks);

                A.areEqual(3, bmarks.size(),
                    "The model list should be 3 long");

                Y.ObjectAssert.areEqual([1, 1, 1], bmarks.get('bid'),
                    "We should get a list of ids from the models");

            },
        });

    Y.Test.Runner.add(model_test);
    Y.Test.Runner.add(modellist_test);
    Y.Test.Runner.run();
});
