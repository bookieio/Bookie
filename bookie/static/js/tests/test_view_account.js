// Create a new YUI instance and populate it with the required modules.
YUI.add('bookie-test-view-account', function (Y) {
    var ns = Y.namespace('bookie.test.view.account');
    ns.suite = new Y.Test.Suite('Account View Tests');
    ns.suite.add(new Y.Test.Case({
        name: "Account View",

        setUp: function () {

        },

        tearDown: function () {
            Y.one('.view').setContent('');
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.AccountView,
                              "Should find an object for Account view");
        },

        testInviteUI: function () {

        }


    }));

    ns.suite.add(new Y.Test.Case({
        name: 'Test the invite bits',
        setUp: function () {
            this.c = new Y.Node.create('<div class="invite_container"/>');
            Y.one('.invites').append(this.c);
        },

        tearDown: function () {
            this.c.remove();
        },

        'the view should init correctly': function () {
            debugger;
            var v = new Y.bookie.InviteView({
                api_cfg: {},
                user: {
                    invite_ct: 10
                }
            });
            this.c.appendChild(v.render());

            Y.Assert.isTrue(
                Y.one('.invite_container').get('innerHTML').search('invite_email') !== -1,
                'We should have the invite email input on the page from our template'
            );
        }
    }));

}, 0.4, {
    requires: [
        'node', 'test', 'bookie-api', 'bookie-view', 'bookie-model', 'node-event-simulate'
    ]
});
