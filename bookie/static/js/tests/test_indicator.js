/* Copyright (c) 2011, Canonical Ltd. All rights reserved. */

YUI().use('console', 'test', 'bookie-indicator', function (Y) {

    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log');

    var tests = new Y.Test.Case({

        name: 'indicator_tests',

        setUp: function () {
            this.div = Y.Node.create('<div/>');
            // Generate an id so we can keep these around as we work.
            this.div.generateID();
            // We want to store this for the testing of the target, after that we
            // can just use this.div.
            this.div_id = this.div.get('id');
            Y.one('body').appendChild(this.div);
        },

        tearDown: function () {
            // Delete the reference to this.div so we can recreate new ones for
            // each test without worry.
            this.div.remove();
            delete this.div;
            if (Y.Lang.isValue(this.indicator)) {
                this.indicator.destroy();
            }
        },

        test_target_attribute: function () {
            // Constrain attribute should be set from passing in target.
            var test_node = Y.one('#' + this.div_id);
            this.indicator = new Y.bookie.Indicator({
                target: test_node
            });
            this.indicator.render();
            Y.Assert.areEqual(test_node, this.indicator.get('target'));
        },

        test_indicator_appended_to_parent: function() {
            // Indicator node is appended to target's parent, rather
            // than target or body.
            var child_div = Y.Node.create('<div/>');
            // We need to create some nesting to really ensure
            // the test is good.
            this.div.appendChild(child_div);
            this.indicator = new Y.bookie.Indicator({
                target: child_div
            });
            this.indicator.render();
            // this.div is actually the parentNode now.
            Y.Assert.areEqual(
                this.div,
                this.indicator.get('boundingBox').get('parentNode'));
        },

        test_indicator_has_loading_icon: function () {
            // The indicator should have a loading image added
            // to the contentBox.
            this.indicator = new Y.bookie.Indicator({
                target: this.div
            });
            this.indicator.render();
            var content = this.indicator.get('boundingBox');
            var test = content.getContent();
            var img = content.one('img');
            Y.Assert.areNotEqual(-1,
                img.get('src').indexOf('/static/images/spinner-big.gif'));
        },

        test_indicator_starts_invisible: function () {
            // Indicator widgets should start hidden.
            this.indicator = new Y.bookie.Indicator({
                target: this.div
            });
            this.indicator.render();
            Y.Assert.isFalse(this.indicator.get('visible'));
            Y.Assert.isTrue(this.indicator.get('boundingBox').hasClass(
                'yui3-bookie.indicator-hidden'));
        },

        test_showing_overlay: function() {
            this.indicator = new Y.bookie.Indicator({
                target: Y.one('#' + this.div_id)
            });
            this.indicator.render();
            this.indicator.show();
            Y.Assert.isTrue(this.indicator.get('visible'));
            Y.Assert.isFalse(this.indicator.get('boundingBox').hasClass(
                'yui3-bookie.Indicator-hidden'));
        },

        test_size_matches_on_show: function() {
            // Indicator should always resize when target changes size.
            this.indicator = new Y.bookie.Indicator({
                target: this.div
            });
            this.indicator.render();
            // Mess with the size of target div.
            var expected_width = 800;
            var expected_height = 600;
            this.div.set('offsetWidth', expected_width);
            this.div.set('offsetHeight', expected_height);
            Y.Assert.areNotEqual(
                expected_width,
                this.indicator.get('boundingBox').get('offsetWidth'));
            Y.Assert.areNotEqual(
                expected_height,
                this.indicator.get('boundingBox').get('offsetHeight'));
            this.indicator.show();
            Y.Assert.areEqual(
                expected_width,
                this.indicator.get('boundingBox').get('offsetWidth'));
            Y.Assert.areEqual(
                expected_height,
                this.indicator.get('boundingBox').get('offsetHeight'));
        },

        test_position_matches_on_set_busy: function() {
            // Indicator should always reposition itself before setBusy.
            this.indicator = new Y.bookie.Indicator({
                target: this.div
            });
            this.indicator.render();
            // Change the position of target div.
            var expected_xy = [100, 300];
            this.div.setXY(expected_xy);
            var actual_xy = this.indicator.get('boundingBox').getXY();
            Y.Assert.areNotEqual(expected_xy[0], actual_xy[0]);
            Y.Assert.areNotEqual(expected_xy[1], actual_xy[1]);
            this.indicator.show();
            var final_xy = this.indicator.get('boundingBox').getXY();
            Y.Assert.areEqual(expected_xy[0], final_xy[0]);
            Y.Assert.areEqual(expected_xy[1], final_xy[1]);
        },


    });

    Y.Test.Runner.add(tests);
    Y.Test.Runner.run();

});
