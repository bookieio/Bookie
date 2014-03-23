YUI.add('bookie-test-tagcontrol', function (Y) {
    var ns = Y.namespace('bookie.test.tagcontrol'),
        A = Y.Assert;

    ns.suite = new Y.Test.Suite('Indicator Tests');

    ns.suite.add(new Y.Test.Case({
        name: "Init Tests",

        setUp: function () {
            Y.one('#container').appendChild(
                Y.Node.create('<input/>')
            );
        },

        tearDown: function () {
            Y.one('#container').setContent('');

            if (this.t) {
                this.t.remove();
                delete this.t;
            }

            if (this.tc) {
                this.tc.destroy();
            }
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.TagControl,
                              "Should find an object for TagControl");
        },

        test_view_attaches: function () {
            // we want to send a required target node to create the widget
            // against
            this.t = Y.one('input');
            this.tc = new Y.bookie.TagControl({
                    srcNode: this.t
                });
            Y.Assert.areEqual(this.t, this.tc.get('srcNode'),
                'The target node should be the one we sent it');
        },

        test_view_replaces: function () {
            // we want to send a required target node to create the widget
            // against
            this.t = Y.one('input');
            this.tc = new Y.bookie.TagControl({
                    srcNode: this.t
                });
            this.tc.render();

            // now let's start checking out some things
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol').size());
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol-item').size());
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol-input').size());
        },

        test_view_add: function () {
            // we want to send a required target node to create the widget
            // against
            this.t = Y.one('input');
            this.tc = new Y.bookie.TagControl({
                srcNode: this.t
            });
            this.tc.render();

            // setup a new tag
            var input = Y.one('.yui3-bookie-tagcontrol-input');
            input.set('value', 'test');

            input.simulate('keyup', {
                keyCode: 32
            });

            // now let's start checking out some things
            Y.Assert.areEqual(2, Y.all('.yui3-bookie-tagcontrol-item').size());
        },

        test_original_syncd: function () {
            // make sure that as we add tags, the original input field is kept
            // in sync with our list of tags
            this.t = Y.one('input');
            this.tc2 = new Y.bookie.TagControl({
                srcNode: this.t
            });
            this.tc2.render();

            // setup a new tag
            var input = Y.one('.yui3-bookie-tagcontrol-input');
            input.set('value', 'test');
            input.simulate('keyup', {
                keyCode: 32
            });

            input.set('value', 'test2');
            input.simulate('keyup', {
                keyCode: 32
            });

            // check the value of the original input
            Y.Assert.areEqual(
                'test test2',
                this.t.get('value'),
                "The input should have our two tags as values: " + this.t.get('value')
            );
        },

        test_view_remove: function () {
            // we want to send a required target node to create the widget
            // against
            this.t = Y.one('input');
            this.tc = new Y.bookie.TagControl({
                srcNode: this.t
            });
            this.tc.render();

            // setup a new tag
            var input = Y.one('.yui3-bookie-tagcontrol-input');
            input.set('value', 'test');

            input.simulate('keyup', {
                keyCode: 32
            });

            // now let's fire the remove click on the tag
            var tags = Y.all('.yui3-bookie-tagcontrol-item'),
                fired = false;
            tags.each(function (t) {
                if (t.getContent() === 'test') {
                    t.simulate('click');
                    fired = true;
                }
            });

            Y.Assert.isTrue(fired, 'Should have found our node');
            // our node should be gone
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol-item').size());
            Y.Assert.areEqual(0, this.tc.get('tags').length);
        },

        test_double_backspace: function () {
            // Hitting delete on the last character removes the previous tag
            this.t = Y.one('input');
            this.tc = new Y.bookie.TagControl({
                srcNode: this.t
            });
            this.tc.render();

            // setup a new tag
            var input = Y.one('.yui3-bookie-tagcontrol-input');
            input.set('value', 'test');

            input.simulate('keyup', {
                keyCode: 32
            });

            // Now let's hit the backspace key and we should lose our new tag.
            input.simulate('keydown', {
                keyCode: 8
            });

            // our node should be gone
            Y.Assert.areEqual(1, Y.all('.yui3-bookie-tagcontrol-item').size());
            Y.Assert.areEqual(0, this.tc.get('tags').length);
        },

        test_initial_tags: function () {
            this.t = Y.one('input');
            this.t.set('value', 'test test2');

            this.tc = new Y.bookie.TagControl({
                srcNode: this.t
            });
            this.tc.render();

            Y.Assert.areEqual(3, Y.all('.yui3-bookie-tagcontrol-item').size());
            Y.Assert.areEqual(2, this.tc.get('tags').length);
        },

        test_duplicate: function () {
 
            this.t = Y.one('input');
            this.tc3 = new Y.bookie.TagControl({
                srcNode: this.t
            });
            this.tc3.render();
 
            // Setup a new tag.
            var input = Y.one('.yui3-bookie-tagcontrol-input');
            input.set('value', 'test');
            input.simulate('keyup', {
                keyCode: 32
            });
 
            input.set('value', 'test2');
            input.simulate('keyup', {
                keyCode: 32
            });
 
            input.set('value', 'test');
            input.simulate('keyup', {
                keyCode: 32
            });
 
            // Test removal of tag at the beginning.
            this.wait(function(){
                Y.Assert.areEqual(
                    'test2 test',
                    this.t.get('value'),
                    "The input should have 2 tags: " + this.t.get('value'));
            }, 200);
 
            input.set('value', 'test3');
            input.simulate('keyup', {
                keyCode: 32
            });
 
            input.set('value', 'test3');
            input.simulate('keyup', {
                keyCode: 32
            });
 
            // Add a duplicate tag at the right end.
            this.wait(function(){
                Y.Assert.areEqual(
                    'test2 test test3',
                    this.t.get('value'),
                    "The input should have 3 tags: " + this.t.get('value'));
            }, 200);
 
            input.set('value', 'test');
            input.simulate('keyup', {
                keyCode: 32
            });
 
            // Test removal of tag in the middle.
            this.wait(function(){
                Y.Assert.areEqual(
                    'test2 test3 test',
                    this.t.get('value'),
                    "The input should have 3 tags: " + this.t.get('value'));
            }, 200);
 
            input.set('value', 'test2');
            input.simulate('keyup', {
                keyCode: 32
            });
 
            // Finally, remove the tag at the front.
            this.wait(function(){
                Y.Assert.areEqual(
                    'test3 test test2',
                    this.t.get('value'),
                    "The input should have 3 tags: " + this.t.get('value'));
            }, 200);
        }
    }));

}, '0.4', {
    requires: [
        'test', 'node-event-simulate', 'bookie-tagcontrol', 'event-valuechange'
    ]
});
