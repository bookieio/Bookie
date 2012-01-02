// Create a new YUI instance and populate it with the required modules.
YUI().use('console', 'test', 'node-event-simulate', 'bookie-tagcontrol', function (Y) {
    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    var view_test = new Y.Test.Case({
        name: "Init Tests",

        setUp: function () {
            Y.one('#container').appendChild(
                Y.Node.create('<input/>')
            );
        },

        tearDown: function () {
            Y.one('#container').setContent('');
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.TagControl,
                              "Should find an object for TagControl");
        },

        test_view_attaches: function () {
            // we want to send a required target node to create the widget
            // against
            var t = Y.one('input'),
                tc = new Y.bookie.TagControl({
                    srcNode: t
                });
            Y.Assert.areEqual(t, tc.get('srcNode'),
                'The target node should be the one we sent it');
        },

        test_view_replaces: function () {
            // we want to send a required target node to create the widget
            // against
            var t = Y.one('input'),
                tc = new Y.bookie.TagControl({
                    srcNode: t
                });
            tc.render();

            // now let's start checking out some things
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol').size());
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol-item').size());
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol-input').size());
        },

        test_view_add: function () {
            // we want to send a required target node to create the widget
            // against
            var t = Y.one('input'),
                tc = new Y.bookie.TagControl({
                    srcNode: t
                });
            tc.render();

            debugger;
            // setup a new tag
            var input = Y.one('.yui3-bookie-tagcontrol-input');
            input.set('value', 'test');

            input.simulate('keyup', {
                keyCode: 32
            });

            // now let's start checking out some things
            Y.Assert.areEqual(2, Y.all('.yui3-bookie-tagcontrol-item').size());
        },
    });

    Y.Test.Runner.add(view_test);

    // more tests here for things like the ajax autocomplete bits

    Y.Test.Runner.run();
});
