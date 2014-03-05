// Create a new YUI instance and populate it with the required modules.
YUI.add('bookie-test-view', function (Y) {
    var ns = Y.namespace('bookie.test.view');
    ns.suite = new Y.Test.Suite('View Tests');

    var bookmark = {

        },
        bmarklist = [
        {
            "username": "admin",
            "updated": "",
            "extended": "",
            "description": "Nuclear Crisis: NRC Says Spent Fuel Pool at Unit 4 Lost Massive Amounts of Water; Japan Disputes Claims",
            "tags": [], "url": "http://feeds.abcnews.com/click.phdo?i=578f79c4656ec416ce71fab58f31fb5b",
            "bid": 11, "total_clicks": 0, "stored": "2011-03-16 20:18:12",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "eeead0f74ff680"},
        {
            "username": "admin",
            "updated": "",
            "extended": "",
            "description": "Oh, Ubisoft: Torrented Their Own Music?",
            "tags": [], "url": "http://feedproxy.google.com/~r/RockPaperShotgun/~3/iYGzlyjrIuM/",
            "bid": 12, "total_clicks": 0, "stored": "2011-03-16 08:00:13",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "b1210b874f52a1"},
        {
            "username": "admin",
            "updated": "",
            "extended": "RT @shiflett: Can we get rid of Flash yet?",
            "description": "Security Advisory for Adobe Flash Player, Adobe Reader and Acrobat (APSA11-01) \u00c2\u00ab  Adobe Product Security Incident Response Team (PSIRT) Blog",
            "tags": [], "url": "http://blogs.adobe.com/psirt/2011/03/security-advisory-for-adobe-flash-player-adobe-reader-and-acrobat-apsa11-01.html",
            "bid": 13, "total_clicks": 0, "stored": "2011-03-15 21:49:58",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "b0e35b6d2fc562"},
        {
            "username": "admin",
            "updated": "",
            "extended": "",
            "description": "Software Carpentry \u00c2\u00bb Literate Programming",
            "tags": [], "url": "http://software-carpentry.org/2011/03/4069/",
            "bid": 14, "total_clicks": 0, "stored": "2011-03-15 18:19:38",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "c70694d2c53494"},
        {
            "username": "admin",
            "updated": "",
            "extended": "RT @davewiner: Adjix automatically saves your links to your S3 bucket when they are created. Every web service should do this.  ...",
            "description": "(500) http://r2",
            "tags": [], "url": "http://r2",
            "bid": 15, "total_clicks": 0, "stored": "2011-03-15 17:39:56",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "af0b78fb818196"}
        ];


    ns.suite.add(new Y.Test.Case({
        name: "View Tests",

        setUp: function () {
        },


        tearDown: function () {
            Y.one('.view').setContent('');
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.BmarkView,
                              "Should find an object for Bmark view");
        },

        test_render_view: function () {
            var model = new Y.bookie.Bmark(bmarklist[0]),
                testview = new Y.bookie.BmarkView({
                    model: model,
                    current_user: 'admin',
                    resource_user: 'admin'
                });

            Y.one('.view').appendChild(testview.render());

            Y.Assert.isTrue(
                Y.one('.view').get('innerHTML').search("eeead0f74ff680") !== -1,
                'We should find the hash id in the rendered html'
            );
        },

        test_render_list: function () {
            var models = new Y.bookie.BmarkList();
            models.add(Y.Array.map(
                bmarklist, function (bmark){
                    return new Y.bookie.Bmark(bmark);
                })
            );

            models.each(function (m, i) {
                var testview = new Y.bookie.BmarkView({model: m});
                Y.one('.view').appendChild(testview.render());
            });

            Y.Assert.isTrue(
                Y.one('.view').get('innerHTML').search("c70694d2c53494") !== -1,
                'We should find the hash id of a middle bmark in the html'
            );
        },

        test_remove_event: function () {
            var model = new Y.bookie.Bmark({
                    url: 'http://google.com'
                }),
                hit = false,
                test = this;

            model.remove = function () {
                hit = true;
            };

            // set the model username to admin so owner is true
            model.set('username', 'admin');

            var testview = new Y.bookie.BmarkView({
                model: model,
                current_user: 'admin',
                resource_user: 'admin'
            });

            var html = testview.render();
            Y.one('.view').appendChild(html);
            var click_points = Y.all('.delete');
            Y.Assert.areEqual(1, click_points.size(),
                "We should have one rendered remove button");

            var button = click_points.pop();
            button.simulate('click');
            Y.Assert.isTrue(hit);

            // we need to wait here for the transition to complete
            this.wait(function () {
                // and verify that our node is now gone
                var click_points = Y.all('.bmark');
                Y.Assert.areEqual(0, click_points.size(),
                    "We shouldn't have any html elements left after deleting");
            }, 700);
        },

        test_missing_edit_when_not_logged_in: function () {
            var model = new Y.bookie.Bmark({
                    url: 'http://google.com'
                }),
                username = null;

            var testview = new Y.bookie.BmarkView({
                model: model,
                current_user: username,
                request_user: 'admin'
            });

            Y.one('.view').appendChild(testview.render());
            var edit_points = Y.all('.edit');

            // there should be no edit points because we're a non logged in
            // user
            Y.Assert.areEqual(0, edit_points.size(),
                "There shouldn't be any edit points for anon users");

        }
    }));

    /**
     * Verify that our paging html is functioning correctly
     *
     */
    ns.suite.add(new Y.Test.Case({
        name: "Paging Tests",

        setUp: function () {
        },

        tearDown: function () {
            Y.one('.pager_test').setContent('');
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.PagerView,
                              "Should find a PagerView");
        },

        test_view_renders: function () {
            // verify that we can render out the html we expect for a pager
            var pager = new Y.bookie.PagerView();
            Y.one('.pager_test').appendChild(pager.render());

            next_points = Y.all('.next');
            Y.Assert.areEqual(1, next_points.size(),
                "Should find one .next link");
        },

        test_fires_next_event: function () {
            // verify that if we click next, we get a custom event
            var hit = false,
                pager = new Y.bookie.PagerView({
                    id: 'test_pager'
                });

            Y.one('.pager_test').appendChild(pager.render());

            var test_event = function (e) {
                hit = true;
            };

            // bind a watcher for the event we're looking for
            Y.on('test_pager:next', test_event);

            // now let's fire a click event on the next link
            Y.one('.next').simulate('click');
            Y.Assert.isTrue(hit, 'Hit should now be true.');
        },

        test_fires_prev_event: function () {
            // verify that if we click prev, we get a custom event
            var hit = false,
                pager = new Y.bookie.PagerView({
                    id: 'test_pager',
                    // by default previous is hidden
                    show_previous: true
                });

            Y.one('.pager_test').appendChild(pager.render());

            var test_event = function (e) {
                hit = true;
            };

            // bind a watcher for the event we're looking for
            Y.on('test_pager:previous', test_event);

            // now let's fire a click event on the prev link
            Y.one('.previous').simulate('click');
            Y.Assert.isTrue(hit, 'Hit should now be true.');
        }

    }));

    ns.suite.add(new Y.Test.Case({
        name: "Bmark List Tests",

        setUp: function () {
        },

        tearDown: function () {
            Y.one('.data_list').setContent('');
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.BmarkListView,
              "Should find a BmarkListView");
        },

        test_view_renders: function () {
            var data_list = new Y.bookie.BmarkListView();

            Y.one('.data_list').appendChild(data_list.render());

            list = Y.all('.bmark_list');
            Y.Assert.areEqual(1, list.size(),
                "Should find one bmark_list container");
        }
    }));

    ns.suite.add(new Y.Test.Case({
        name: 'Options View',
        setUp: function () {
        },

        tearDown: function () {
        },

        test_exists: function () {
            Y.Assert.isObject(Y.bookie.OptionsView,
                'We should be able to find the OptionsView object');
        }
    }));

    ns.suite.add(new Y.Test.Case({
        name: 'Forgot password',

        test_error_message: function () {
            var test = this,
                resp = '{"error": "Please submit a valid address"}';

            // Stub out the API call with a fake response.
            var old_method = Y.bookie.Api.route.SuspendUser;
            Y.bookie.Api.route.SuspendUser = function(cfg) {
                return {
                    call: function(cfg) {
                      cfg.error(null, null, {
                          response: resp
                      });
                    }
                };
            };

            var login = new Y.bookie.LoginView();
            login.render();

            // The error message should be shown to the user.
            // simulate click on submit button
            Y.one('#submit_forgotten').simulate('click');
            this.wait(function() {
                // Assert that it returns error
                var message = Y.one('#forgotten_msg');

                Y.Assert.areEqual(
                    "Please submit a valid address",
                    message.get('innerHTML'));

                // And verify that the message changed after the ajax
                // call completes.
                Y.Assert.areEqual(
                    message.getAttribute('class'),
                    'error');

                Y.bookie.Api.route.SuspendUser = old_method;
            }, 500);
        },
    }));


    ns.suite.add(new Y.Test.Case({
        name: 'Url Edit Tests',

        test_Url_edit: function () {
            var page = new Y.bookie.BmarkEditView();
            page.render();
            Y.one('#url').set('value','google.com');
            Y.one('#url').simulate('blur');
            editedurl = Y.one('#url').get('value');
            Y.Assert.areEqual('http://google.com', editedurl,
                'Should edit the url');
        }
    }));


}, '0.4', {
    requires: [
        'test', 'bookie-api', 'bookie-view', 'bookie-model', 'node-event-simulate'
    ]
});
