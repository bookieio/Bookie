/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */
YUI.add('bookie-model', function (Y) {
    var _ = Y.Lang.substitute;

    Y.namespace('bookie');

    Y.bookie.Bmark = Y.Base.create('bookie-bmark',
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
        },
        {
            ATTRS: {
                'bid': {},
                'clicks': 0,
                'description': {},
                'hash_id': {},
                'inserted_by': null,
                'tag_str': '',
                'tags': [],
                'total_clicks': 0,
                'url': '',
                'username': '',
                'extended': {},
                'stored': {
                    // we need to turn a string from json into a Date object
                    setter: function (val, name) {
                        return new Date(val);
                    }
                },
                'updated': {
                    // we need to turn a string from json into a Date object
                    setter: function (val, name) {
                        return new Date(val);
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

        });

    Y.bookie.BmarkList = Y.Base.create('bookie-bmark-list', Y.ModelList, [], {
        // Add prototype properties and methods for your List here if desired. These
        // will be available to all instances of your List.
        model: Y.bookie.Bmark,


    });


}, '0.1.0' /* module version */, {
    requires: ['base', 'model', 'model-list']
});
