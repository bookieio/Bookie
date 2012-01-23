/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */
YUI.add('bookie-model', function (Y) {
    var _ = Y.substitute,
        ns = Y.namespace('bookie');

   var TZ = '-05:00';

    ns.Bmark = Y.Base.create('bookie-bmark',
        Y.Model,
        [],
        {
            /**
             * Maps to destroy with delete: true
             *
             */
            remove: function (callback) {
                this.destroy({delete: true}, callback);
            },

            /**
             * Handle remote updates to the server for the model instance
             *
             */
            sync: function (action, options, callback) {
                switch (action) {

                    case 'delete':
                        // perform a delete api request to the server
                        var delete_cfg = this.api_cfg;
                        delete_cfg.hash_id = this.get('hash_id');
                        var api = new Y.bookie.Api.route.UserBmarkDelete(delete_cfg);
                        api.call({
                            success: callback
                        });
                };
            }
        },
        {
            ATTRS: {
                'bid': {},
                'clicks': {
                    value: 0
                },
                'description': {},
                'hash_id': {},
                'inserted_by': {},
                'owner': {
                    value: false
                },
                'tag_str': {
                    value: ''
                },
                'tags': {
                    value: []
                },
                'total_clicks': {
                    value: 0
                },
                'url': {
                    value: ''
                },
                'username': {
                    value: ''
                },
                'extended': {},
                'stored': {
                    // we need to turn a string from json into a Date object
                    setter: function (val, name) {
                        return new Date(val.replace(' ', 'T') + TZ);
                    }
                },
                'updated': {
                    // we need to turn a string from json into a Date object
                    setter: function (val, name) {
                        return new Date(val.replace(' ', 'T') + TZ);
                    }
                },

                // clean date for the bmark in month/date
                'dateinfo': {
                    // we want to return a formatted version of stored
                    getter: function (val) {
                        var val = this.get('stored');
                        if (val) {
                            return (val.getMonth() + 1) + "/" + val.getDate();
                        } else {
                            return val;
                        }
                    }
                },

                // clean date in 3/13/2011 15:45
                'prettystored': {
                    // we want to return a formatted version of stored
                    getter: function (val) {
                        var val = this.get('stored');
                        if (val) {
                            return _("{month}/{date}/{year} {hours}:{minutes}", {
                                     'month': val.getMonth() + 1,
                                     'date': val.getDate(),
                                     'year': val.getFullYear(),
                                     'hours': val.getHours(),
                                     'minutes': val.getMinutes()
                            });
                        } else {
                            return val;
                        }
                    }
                },
           },
        }
    );

    ns.BmarkList = Y.Base.create('bookie-bmark-list', Y.ModelList, [], {
        model: Y.bookie.Bmark,
    });


    ns.PagerModel = Y.Base.create('bookie-pager', Y.Model, [], {
        next: function () {
            this.set('page', this.get('page') + 1);
        },

        previous: function () {
            var cpage = this.get('page');

            if (cpage > 0) {
                this.set('page', this.get('page') - 1);
            } else {
                this.set('page', 0);
            }
        }

    }, {
        ATTRS: {
            count: {
                value: 20
            },
            page: {
                value: 0
            },
            with_content: {
                value: false
            }
        }
    });



}, '0.1.0' /* module version */, {
    requires: ['base', 'model', 'model-list', 'substitute']
});
