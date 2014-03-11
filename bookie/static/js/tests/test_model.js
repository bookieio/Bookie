YUI.add('bookie-test-model', function (Y) {
    var ns = Y.namespace('bookie.test.model'),
        A = Y.Assert;

    ns.suite = new Y.Test.Suite('Model Tests');

    function test_model() {
        return new Y.bookie.Bmark({
            'bid': 1,
            'hash_id': generate_random_string(),
            'description': "description",
            'extended': "longer description",
            'stored': "2011-11-10 20:57:40.273044",
            'updated': "2011-11-11 20:57:40.273044",
            'prettystored': ""
        });
    }

    function generate_random_string() {
        var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
        var string_length = 8;
        var randomstring = '';
        for (var i=0; i<string_length; i++) {
            var rnum = Math.floor(Math.random() * chars.length);
            randomstring += chars.substring(rnum,rnum+1);
        }
        return randomstring;
    }

    ns.suite.add(new Y.Test.Case({
        name: "Model Tests",

        empty_model: function () {
            return new Y.bookie.Bmark({
                'bid': "",
                'hash_id': "",
                'description': "",
                'extended': "",
                'stored': "2011-11-10 20:57:40.273044",
                'updated': "2011-11-11 20:57:40.273044",
                'prettystored': "",
                'uesrname': ""
            });
        },

        "Bmark model should exist": function () {
            A.isObject(
                Y.bookie.Bmark,
                "Should find an object for Bmark model"
            );
        },

        "model date getters should format correctly": function () {
            var bmark = test_model();
            A.isInstanceOf(Date, bmark.get('stored_date'),
                "Stored should be converted from string to Date object");
        },

        "model domain should parse out the url properly": function () {
            var b = new Y.bookie.Bmark({
                url: 'http://dotfiles.github.com/test#something'
            });
            Y.Assert.areEqual('github.com', b.get('domain'));
        },

        "calling remove should run destroy": function () {
            var bmark = test_model();

            // override the destroy method to make sure it gets called
            // right
            bmark.destroy = function (opts, callback) {
                hit = true;
                A.isTrue(opts.delete, "Delete should be true in the options");
            };

            bmark.remove();

            A.isTrue(hit, "We should have hit the destroy function");
        },

        "calling remove should fire sync with delete action": function () {
            var bmark = test_model();

            // override the sync method to make sure it gets called
            // right
            bmark.sync = function (action, opts, callback) {
                hit = true;
                A.areEqual(action, 'delete', 'Delete should be true in the options');
            };

            bmark.remove();
            A.isTrue(hit, "We should have hit the sync with delete");
        },

        "creating a bmark with a url should get a hash_id": function () {
            var b = new Y.bookie.Bmark({
                url: 'http://google.com'
            });
            Y.Assert.areEqual('aa2239c17609b2', b.get('hash_id'));
        },

        "updating the url should change the hash_id": function () {
            var b = new Y.bookie.Bmark({
                url: 'http://google.com'
            });
            b.set('url', 'http://bmark.us');
            Y.Assert.areEqual('c5c21717c99797', b.get('hash_id'));
        }
    }));


    ns.suite.add(new Y.Test.Case({
        name: "Model Tests",
        test_init: function () {
            var json_bmarks = [
                test_model(),
                test_model(),
                test_model()
            ];

            var bmarks = new Y.bookie.BmarkList();
            Y.Array.each(json_bmarks, function (b) {
                bmarks.add(b);
            });

            A.areEqual(3, bmarks.size(),
                "The model list should be 3 long");

            Y.ObjectAssert.areEqual([1, 1, 1], bmarks.get('bid'),
                "We should get a list of ids from the models");

        }
    }));


    ns.suite.add(new Y.Test.Case({
        name: "Pager Tests",
        test_init: function () {
            var p = new Y.bookie.PagerModel();

            A.areEqual(0, p.get('page'),
                'The page should start out at 1');
            A.areEqual(20, p.get('count'),
                'The default count is 20');
        },

        test_decrement_one: function () {
            var p = new Y.bookie.PagerModel();

            p.previous();
            A.areEqual(0, p.get('page'),
                'The page should never get below 1');
        },

        test_increment: function () {
            var p = new Y.bookie.PagerModel();

            p.next();
            A.areEqual(1, p.get('page'),
                'The page should increment to 1');
        },

        test_feeding_attrs: function () {
            var p = new Y.bookie.PagerModel({
                count: 5,
                page: 8,
                with_content: true
            });

            p.next();
            p.next();

            A.areEqual(10, p.get('page'),
                'The page should be up to 10');
            A.areEqual(5, p.get('count'),
                'The count should be at 5 per page');
            A.isTrue(p.get('with_content'),
                'We should be fetching with content');
        }
    }));


    ns.suite.add(new Y.Test.Case({
        name: "Tests for the Options model",
        _local_storage_keys: [
            'api_url',
            'api_username',
            'api_key',
            'cache_content'
        ],

        setUp: function () {

        },

        tearDown: function () {
            Y.Array.each(this._local_storage_keys, function (k) {
                localStorage.removeItem(k);
            });
        },

        test_init: function () {
            A.isObject(Y.bookie.OptionsModel,
                'We should be able to see the OptionsModel in the namespace');
        },

        test_defaults: function () {
            // We should have some sane defaults for our config
            var m = new Y.bookie.OptionsModel();

            A.areEqual('https://bmark.us/api/v1', m.get('api_url'));
            A.areEqual('username', m.get('api_username'));
            A.areEqual('XXXXXX', m.get('api_key'));
            A.areEqual('true', m.get('cache_content'));
        },

        test_save: function () {
            // When we tell a model to save, it should be writing out to
            // our localStorage for us to keep a hold of
            var m = new Y.bookie.OptionsModel();
            m.save();

            A.areEqual('https://bmark.us/api/v1', localStorage.getItem('api_url'));
            A.areEqual('username', localStorage.getItem('api_username'));
            A.areEqual('XXXXXX', localStorage.getItem('api_key'));
            A.areEqual('true', localStorage.getItem('cache_content'));
        },

        test_load: function () {
            // we should be able to retrieve the settings from the
            // localStorage
            localStorage.setItem('api_url', 'test.com');
            localStorage.setItem('api_username', 'test');
            localStorage.setItem('api_key', 'test123');
            localStorage.setItem('cache_content', 'false');

            var m = new Y.bookie.OptionsModel();
            m.load();

            A.areEqual('test.com', m.get('api_url'));
            A.areEqual('test', m.get('api_username'));
            A.areEqual('test123', m.get('api_key'));
            A.areEqual('false', m.get('cache_content'));
        }
    }));

}, '0.4', {
    requires: [
        'test', 'bookie-model', 'bookie-api'
    ]
});
