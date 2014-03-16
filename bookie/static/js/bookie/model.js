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

    // Copyright (C) 2011 by Will Tomlins
    //
    // Github profile: http://github.com/layam
    //
    // Permission is hereby granted, free of charge, to any person obtaining a copy
    // of this software and associated documentation files (the "Software"), to deal
    // in the Software without restriction, including without limitation the rights
    // to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    // copies of the Software, and to permit persons to whom the Software is
    // furnished to do so, subject to the following conditions:
    //
    // The above copyright notice and this permission notice shall be included in
    // all copies or substantial portions of the Software.
    //
    // THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    // IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    // FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    // AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    // LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    // OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    // THE SOFTWARE.


    function humanized_time_span(date, ref_date, date_formats, time_units) {

      //Date Formats must be be ordered
      // smallest -> largest and must end in a format with ceiling of null
      date_formats = date_formats || {
        past: [
          { ceiling: 60, text: "$seconds seconds ago" },
          { ceiling: 3600, text: "$minutes minutes ago" },
          { ceiling: 86400, text: "$hours hours ago" },
          { ceiling: 2629744, text: "$days days ago" },
          { ceiling: 31556926, text: "$months months ago" },
          { ceiling: null, text: "$years years ago" }
        ],
        future: [
          { ceiling: 60, text: "in $seconds seconds" },
          { ceiling: 3600, text: "in $minutes minutes" },
          { ceiling: 86400, text: "in $hours hours" },
          { ceiling: 2629744, text: "in $days days" },
          { ceiling: 31556926, text: "in $months months" },
          { ceiling: null, text: "in $years years" }
        ]
      };
      //Time units must be be ordered largest -> smallest
      time_units = time_units || [
        [31556926, 'years'],
        [2629744, 'months'],
        [86400, 'days'],
        [3600, 'hours'],
        [60, 'minutes'],
        [1, 'seconds']
      ];

      date = new Date(date);
      ref_date = ref_date ? new Date(ref_date) : new Date();
      var seconds_difference = (ref_date - date) / 1000;

      var tense = 'past';
      if (seconds_difference < 0) {
        tense = 'future';
        seconds_difference = 0-seconds_difference;
      }

      function get_format() {
        for (var i=0; i<date_formats[tense].length; i++) {
          if (date_formats[tense][i].ceiling === null ||
              seconds_difference <= date_formats[tense][i].ceiling) {
            return date_formats[tense][i];
          }
        }
        return null;
      }

      function get_time_breakdown() {
        var seconds = seconds_difference;
        var breakdown = {};
        for(var i=0; i<time_units.length; i++) {
          var occurences_of_unit = Math.floor(seconds / time_units[i][0]);
          seconds = seconds - (time_units[i][0] * occurences_of_unit);
          breakdown[time_units[i][1]] = occurences_of_unit;
        }
        return breakdown;
      }

      function render_date(date_format) {
        var breakdown = get_time_breakdown();
        var time_ago_text = date_format.text.replace(/\$(\w+)/g, function() {
          return breakdown[arguments[1]];
        });
        return depluralize_time_ago_text(time_ago_text, breakdown);
      }

      function depluralize_time_ago_text(time_ago_text, breakdown) {
        for(var i in breakdown) {
          if (breakdown[i] == 1) {
            var regexp = new RegExp("\\b"+i+"\\b");
            time_ago_text = time_ago_text.replace(regexp, function() {
              return arguments[0].replace(/s\b/g, '');
            });
          }
        }
        return time_ago_text;
      }

      return render_date(get_format());
    }


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
             * Create is only used for objects that don't have an id and most
             * of the time we instantiate it with a hash_id so this is
             * really never available.
             *
             * @method _create
             * @param {Object} options
             * @param {Function} callback
             * @private
             *
             */
            _create: function (options, callback) {
                console.log('did you really get this? See my comment');
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
               var delete_cfg = this.get('api_cfg'),
                   api;

               delete_cfg.hash_id = this.get('hash_id');
               api = new Y.bookie.Api.route.UserBmarkDelete(delete_cfg);
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
                var that = this,
                    api;
                // the bid is required in order to fetch the bookmark from the
                // api.
                if (!options.hash_id) {
                    throw "Could not load bookmark without a hash_id property!";
                }

                api = new Y.bookie.Api.route.Bmark(Y.merge(this.get('api_cfg'), options));
                api.call({
                    'success': function (data, request) {
                        that.setAttrs(data.bmark);

                        // if there's a last in the data we need to set that
                        // as well
                        if (data.last) {
                            that.set('last', data.last);
                        }
                    },
                    'error': function (data, status_str, response, args) {
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
                    data = that.getAttrs(),
                    tmp,
                    api;

                // remove the api cfg from the data, that doesn't need to get
                // sent in the url
                delete data.api_cfg;

                // the Bookie api expects the tags to be a string, so put
                // those together and replace the data with it.
                tmp = Y.Array.reduce(data.tags, '', function (prev, cur, idx, arr) {
                    return [prev, cur].join(' ');
                });

                data.tags = tmp;

                api = new Y.bookie.Api.route.UserBmarkSave(

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
                this.destroy({
                    delete: true
                }, callback);
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
                }
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

                'domain': {
                    getter: function () {
                        var url = this.get('url');
                        var domain = url.replace('http://','').replace('https://','').split(/[/?#]/)[0];
                        var spl = domain.split('.');
                        return [spl[spl.length-2], spl[spl.length-1]].join('.');
                    }
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
                    getter: function(val) {
                      if (val) {
                          return val.replace(/-/g, '/') + " UTC";
                      } else {
                          return undefined;
                      }
                    }

                },

                'stored_date': {
                    getter: function() {
                        var stored = this.get('stored');
                        if (stored) {
                            return new Date(stored);
                        }

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
                        return new Date(val + " UTC");
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
                        var ret,
                            stored = this.get('stored');
                        if (stored) {
                            ret = humanized_time_span(stored);
                        } else {
                            ret = stored;
                        }
                        return ret;
                    }
                }
           }
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
        model: Y.bookie.Bmark
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
            var ret,
                found = localStorage.getItem(key);
            if (found === null) {
                ret = def;
            } else {
                ret = found;
            }
            return ret;
        },

        get_apicfg: function () {
            return {
                url: this.get('api_url'),
                username: this.get('api_username'),
                api_key: this.get('api_key'),
                last_bmark: this.get('last_bmark')
            };
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
            }
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

}, '0.1.0', {
    requires: [
        'base',
        'bookie-hash',
        'model',
        'model-list',
        'substitute'
    ]
});
