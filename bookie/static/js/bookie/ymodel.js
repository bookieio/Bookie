/*jslint eqeqeq: false, browser: true, debug: true, onevar: true,
         plusplus: false, newcap: false, */
/*global _: false, window: false, self: false, escape: false, */
/**
 * Bookie Model objects
 *
 * @namespace bookie
 * @module model
 *
 */
YUI.add('bookie-model', function (Y) {
    var _ = Y.substitute,
        ns = Y.namespace('bookie');

    var TZ = '-05:00';

    /**
     * Representing a single bmark database object
     *
     * @class Bmark
     * @extends Y.Model
     *
     */
    ns.Bmark = Y.Base.create('bookie-bmark',
        Y.Model,
        [], {

            idAttribute: 'hash_id',

            /**
             * Handle the save() event for objects that don't yet have an id.
             *
             * @method _create
             * @param {Object} options
             * @param {Function} callback
             * @private
             *
             */
            _create: function (options, callback) {
                console.log('in create...nothing to see here yet');
            },

            /**
             * Handle the delete() event for objects.
             *
             * @method _delete
             * @param {Object} options
             * @param {Function} callback
             * @private
             *
             */
            _delete: function (options, callback) {
               // perform a delete api request to the server
               var delete_cfg = this.api_cfg;
               delete_cfg.hash_id = this.get('hash_id');
               var api = new Y.bookie.Api.route.UserBmarkDelete(delete_cfg);
               api.call({
                   success: callback
               });
            },

            /**
             * Handle the read() event for objects and load it from storage.
             *
             * We need to fetch it from the api.
             *
             * @method _read
             * @param {Object} options
             * @param {Function} callback
             * @private
             *
             */
            _read: function (options, callback) {
                var that = this;
                // the bid is required in order to fetch the bookmark from the
                // api.
                if (!options.hash_id) {
                    throw "Could not load bookmark without a hash_id property!";
                }

                var api = new Y.bookie.Api.route.Bmark(Y.merge(this.get('api_cfg'), options));
                api.call({
                    'success': function (data, request) {
                        that.setAttrs(data.bmark);

                        // if there's a last in the data we need to set that
                        // as well
                        if (data.last) {
                            that.set('last', data.last);
                        }
                    },
                    'error': function (data, status_str, response, arguments) {
                        // We might also get a last bookmark data on not
                        // found error condition. If we've got a last record,
                        // go ahead and set it on the current bookmark.
                        if (data.last) {
                            that.set('last', data.last);
                        }
                    }
                });
            },

            /**
             * Handle the save() event for objects that have an id and write it
             * out to storage.
             *
             * @method _update
             * @param {Object} options
             * @param {Function} callback
             * @private
             *
             */
            _update: function (options, callback) {
                // we need to prepare an api request with the data to update
                var that = this,
                    data = that.getAttrs();

                // remove the api cfg from the data, that doesn't need to get
                // sent in the url
                delete data.api_cfg;

                // the Bookie api expects the tags to be a string, so put
                // those together and replace the data with it.
                var tmp = Y.Array.reduce(data.tags, '', function (prev, cur, idx, arr) {
                    return [prev, cur].join(' ');
                });
                data.tags = tmp;

                var api = new Y.bookie.Api.route.UserBmarkSave(

                    Y.merge(this.get('api_cfg'), {
                        model: data
                    })
                );

                api.call({
                    success: callback
                });
            },

            /**
             * General initializer, we need this to hash urls passed in during
             * construction.
             *
             * @method initializer
             * @param {Object} cfg
             *
             */
            initializer: function (cfg) {
                // If there's a url in here, make sure we store the hash_id
                // since that's the key we need for future api calls and such.
                if (cfg.url) {
                    this.set('hash_id', Y.bookie.Hash.hash_url(cfg.url));
                }
            },

            /**
             * Maps to destroy with delete: true to remove a bookmark from the
             * system.
             *
             * @method remove
             * @param {Function} callback
             *
             */
            remove: function (callback) {
                this.destroy({delete: true}, callback);
            },

            /**
             * Handle sync'ing the model object to full storage, in this case
             * updating the server with changes.
             *
             * Currently only supported the `delete` action and makes the
             * async call to the API to remove the bookmark.
             *
             * @method sync
             * @param {String} action
             * @param {Object} options
             * @param {Function} callback
             *
             */
            sync: function (action, options, callback) {
                switch (action) {
                    case 'create':
                        this._create(options, callback);
                        return;

                    case 'delete':
                        this._delete(options, callback);
                        return;

                    case 'read':
                        this._read(options, callback);
                        return;

                    case 'update':
                        this._update(options, callback);
                        return;

                    default:
                        console.log('Invalid action to Bmark Model ' + action);
                        callback('Invalid action');
                };
            }
        },
        {
            ATTRS: {
                /**
                 * @attribute api_cfg
                 * @default undefined
                 * @type Object
                 *
                 */
                api_cfg: {

                },

                /**
                 * @attribute bid
                 * @default undefined
                 * @type Integer
                 *
                 */
                'bid': {},

                /**
                 * @attribute clicks
                 * @default 0
                 * @type Integer
                 *
                 */
                'clicks': {
                    value: 0
                },

                /**
                 * @attribute description
                 * @default ''
                 * @type String
                 *
                 */
                'description': {
                    value: ''
                },

                /**
                 * @attribute hash_id
                 * @default undefined
                 * @type String
                 *
                 */
                'hash_id': {},

                /**
                 * @attribute inserted_by
                 * @default undefined
                 * @type String
                 *
                 */
                'inserted_by': {},

                /**
                 * If the request says to, we'll set the last bookmark we
                 * stored here in the last attribute.
                 *
                 * This is used to help suggested tags using the tags we've
                 * set on recent bookmarks.
                 *
                 * @attribute last
                 * @default undefined
                 * @type Bmark
                 *
                 */
                'last': {
                },

                /**
                 * @attribute owner
                 * @default false
                 * @type Boolean
                 *
                 */
                'owner': {
                    value: false
                },

                /**
                 * @attribute tag_str
                 * @default ''
                 * @type String
                 *
                 */
                'tag_str': {
                    value: ''
                },

                /**
                 * @attribute tags
                 * @default []
                 * @type Array
                 *
                 */
                'tags': {
                    value: []
                },

                /**
                 * @attribute total_clicks
                 * @default 0
                 * @type Integer
                 *
                 */
                'total_clicks': {
                    value: 0
                },

                /**
                 * @attribute url
                 * @default ''
                 * @type String
                 *
                 */
                'url': {
                    value: '',
                    setter: function (val) {
                        // whenever we update the url, hash it and update our
                        // hash_id
                        var hashed = Y.bookie.Hash.hash_url(val);
                        this.set('hash_id', hashed);

                        return val;
                    }
                },

                /**
                 * @attribute username
                 * @default ''
                 * @type String
                 *
                 */
                'username': {
                    value: ''
                },

                /**
                 * @attribute extended
                 * @default ''
                 * @type String
                 *
                 */
                'extended': {
                    value: ''
                },

                /**
                 * @attribute stored
                 * @default undefined
                 * @type Date
                 *
                 */
                'stored': {
                    // we need to turn a string from json into a Date object
                    setter: function (val, name) {
                        return new Date(val.replace(' ', 'T') + TZ);
                    }
                },

                /**
                 * @attribute updated
                 * @default undefined
                 * @type Date
                 *
                 */
                'updated': {
                    // we need to turn a string from json into a Date object
                    setter: function (val, name) {
                        return new Date(val.replace(' ', 'T') + TZ);
                    }
                },

                /**
                 * Clean date for the bmark in month/date format.
                 *
                 * @attribute dateinfo
                 * @readonly
                 * @type String
                 *
                 */
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

                /**
                 * Cleaned up pretty version of the stored date used in the UI
                 *
                 * @attribute prettystored
                 * @type String
                 * @readonly
                 *
                 */
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

    /**
     * Y.ModelList for a seriesof Bookmarks
     *
     * @class BmarkList
     * @extends Y.ModelList
     *
     */
    ns.BmarkList = Y.Base.create('bookie-bmark-list', Y.ModelList, [], {
        model: Y.bookie.Bmark,
    });


    /**
     * Model to represent the paging information for some state.
     *
     * @class PagerModel
     * @extends Y.Model
     *
     */
    ns.PagerModel = Y.Base.create('bookie-pager', Y.Model, [], {
        /**
         * Advance the page of the current Pager.
         *
         * @method next
         *
         */
        next: function () {
            this.set('page', this.get('page') + 1);
        },

        /**
         * Decrement the page of the current Pager.
         *
         * @method previous
         *
         */
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
            /**
             * @attribute count
             * @default 20
             * @type Integer
             *
             */
            count: {
                value: 20
            },

            /**
             *
             * @attribute page
             * @default 0
             * @type Integer
             *
             */
            page: {
                value: 0
            },

            /**
             * @attribute with_content
             * @default false
             * @type Boolean
             *
             */
            with_content: {
                value: false
            }
        }
    });


    /**
     * Model object to help us store/handle the options for our extension.
     *
     * @class OptionsModel
     * @extends Y.Model
     *
     */
    ns.OptionsModel = Y.Base.create('bookie-options', Y.Model, [], {
        /**
         * Handle the save() event for objects that don't yet have an id.
         *
         * @method _create
         * @param {Object} options
         * @param {Function} callback
         * @private
         *
         */
        _create: function (options, callback) {

        },

        /**
         * Handle the delete() event for objects.
         *
         * @method _delete
         * @param {Object} options
         * @param {Function} callback
         * @private
         *
         */
        _delete: function (options, callback) {

        },

        /**
         * Handle the read() event for objects and load it from storage.
         *
         * @method _read
         * @param {Object} options
         * @param {Function} callback
         * @private
         *
         */
        _read: function (options, callback) {
            this.set('api_url',
                this._get_data('api_url', this.get('api_url')));
           this.set('api_username',
                this._get_data('api_username', this.get('api_username')));
           this.set('api_key',
                this._get_data('api_key', this.get('api_key')));
           this.set('cache_content',
                this._get_data('cache_content', this.get('cache_content')));
           this.set('last_bmark',
                this._get_data('last_bmark', this.get('last_bmark')));
        },


        /**
         * Handle the save() event for objects that have an id and write it
         * out to storage.
         *
         * @method _update
         * @param {Object} options
         * @param {Function} callback
         * @private
         *
         */
        _update: function (options, callback) {
            localStorage.setItem('api_url', this.get('api_url'));
            localStorage.setItem('api_username', this.get('api_username'));
            localStorage.setItem('api_key', this.get('api_key'));
            localStorage.setItem('cache_content', this.get('cache_content'));
            localStorage.setItem('last_bmark', this.get('last_bmark'));
        },

        /**
         * A helper to getting data from localStorage, but using the passed in
         * default if the key isn't found.
         *
         * @method _get_data
         * @param {String} key
         * @param def
         * @private
         *
         */
        _get_data: function (key, def) {
            var found = localStorage.getItem(key);
            if (found === null) {
                return def;
            } else {
                return found;
            }
        },

        get_apicfg: function () {
            return {
                url: this.get('api_url'),
                username: this.get('api_username'),
                api_key: this.get('api_key'),
                last_bmark: this.get('last_bmark')
            }
        },

        /**
         * Load the Options data from the localStorage. This over rides the
         * Y.Momdel load() method and handles making sure sync is getting the
         * right data.
         *
         * @method load
         *
         */
        load: function (callback) {
            this.sync('read', {}, callback);
        },

        /**
         * Sync is called for save, load, destroy in order facilitate updating
         * the model with a storage mechanism. In our case, we want to
         * load/store the values from the localStorage.
         *
         * @method sync
         * @param {String} action create, read, update, delete
         * @param {Object} options
         * @param {Function} callback
         *
         */
        sync: function (action, options, callback) {
            switch (action) {
                case 'create':
                    this._create(options, callback);
                    return;

                case 'delete':
                    this._delete(options, callback);
                    return;

                case 'read':
                    this._read(options, callback);
                    return;

                case 'update':
                    this._update(options, callback);
                    return;

                default:
                    console.log('Invalid action to OptionsModel ' + action);
                    callback('Invalid action');
            };
        }
    }, {
        ATTRS: {
            /**
             * @attribute id
             * @default 1
             * @type Integer
             * @readOnly
             *
             */
            id: {
                value: 1,
                readOnly: true
            },

            /**
             * @attribute api_url
             * @default 'https://bmark.us'
             * @type String
             *
             */
            api_url: {
                value: 'https://bmark.us/api/v1'
            },

            /**
             * @attribute api_username
             * @default 'username'
             * @type String
             *
             */
            api_username: {
                value: 'username'
            },

            /**
             * @attribute api_key
             * @default 'XXXXXX'
             * @type String
             *
             */
            api_key: {
                value: 'XXXXXX'
            },

            /**
             * This is a bool value we store as a string since localStorage
             * can only handle strings. So basically we're going to be using
             * lowercase strings of 'true' and 'false'. Sucks I know...
             *
             * @attribute cache_content
             * @default 'true'
             * @type String
             *
             */
            cache_content: {
                value: 'true'
            },

            /**
             * Should we get the last bookmark when we're setting up the api
             * cfg?
             * @attribute last_bmark
             * @default true
             * @type Boolean
             *
             */
            last_bmark: {
                value: true
            }
        }
    });

}, '0.1.0' /* module version */, {
    requires: ['base', 'model', 'model-list', 'substitute', 'bookie-hash']
});
