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
        name: "Account Information Change",

        setUp: function() {
            this.view = new Y.bookie.AccountInfoView();
            this.view.render();
        },

        tearDown: function() {
            this.view.destroy();
            Y.one('#email').setAttribute('value', '');
            Y.one('#name').setAttribute('value', '');
        },

        test_invalid_name: function () {
            Y.one('#submit_account_change').simulate('click');
            this.wait(function() {

                var message = Y.one('#account_msg');
                Y.Assert.areEqual(
                    "Please enter valid name",
                    message.get('innerHTML'));
                Y.Assert.areEqual(
                    message.getAttribute('class'),
                    'error');
            },500);
        },

        test_invalid_email: function () {
            Y.one('#name').setAttribute('value', 'admin');
            Y.one('#submit_account_change').simulate('click');

            this.wait(function() {
                var message = Y.one('#account_msg');
                Y.Assert.areEqual(
                    "Please enter valid email address",
                    message.get('innerHTML'));
                Y.Assert.areEqual(
                    message.getAttribute('class'),
                    'error');
            },500);
        }
    }));


    ns.suite.add(new Y.Test.Case({
        name: 'Test the invite bits',
        setUp: function () {
            this.c = new Y.Node.create('<div id="invite_container"/>');
            Y.one('.invites').append(this.c);
        },

        tearDown: function () {
            this.c.destroy();
            delete this.c;
            Y.one('.invites').setContent('');
        },

        'the view should init correctly': function () {
            var v = new Y.bookie.InviteView({
                api_cfg: {},
                user: {
                    invite_ct: 10
                }
            });
            this.c.appendChild(v.render());

            Y.Assert.isTrue(
                Y.one('#invite_container').get('innerHTML').search('invite_email') !== -1,
                'We should have the invite email input on the page from our template'
            );
        },

        'submitting invite should fire api call': function () {
            var called = false;
                old_invite = Y.bookie.InviteView.prototype.invite;

            Y.bookie.InviteView.prototype.invite = function (ev) {
                called = true;
            };

            v = new Y.bookie.InviteView({
                api_cfg: {

                },
                user: {
                    invite_ct: 10
                }
            });

            this.c.appendChild(v.render());
            var input = Y.one('#send_invite');
            input.simulate('click', {});

            Y.Assert.isTrue(called,
                'should have fired our hook by submitting the invite form.');

            // restore the invite method
            Y.bookie.InviteView.prototype.invite = old_invite;
        }
    }));

}, 0.4, {
    requires: [
        'node', 'test', 'bookie-api', 'bookie-view', 'bookie-model', 'event-simulate', 'node-event-simulate'
    ]
});
