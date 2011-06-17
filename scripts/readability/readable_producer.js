/**
 * Readable Producer:
 * Check with the bookie api for bookmarks that we still need to parse
 * Process those, fetch their content, and pass to the consumer via the
 * beanstalkd message queue
 *
 * Requirements:
 *     npm install nodestalker request nlogger
 *
 *
 */
var bs = require('nodestalker'),
    http = require('http'),
    log = require('nlogger').logger(module),
    qs = require('querystring'),
    req = require('get'),
    url = require('url'),
    util = require('util');

var bean_client = bs.Client(),
    inspect = util.inspect,
    API = "http://127.0.0.1:6543/api/v1/bmarks",
    TIMEOUT = 25;

/**
 * Bind this to the global connection instance of the queue
 *
 */
bean_client.addListener('error', function(data) {
    log.error('QUEUE ERROR');
    log.error(data);
});

bean_client.use('default').onSuccess(function (data) {
    log.info('connected to default tube for queue');
});


/**
 * Used to hack the .extend method onto objects for options and such
 *
 */
Object.defineProperty(Object.prototype, "extend", {
    enumerable: false,
    value: function(from) {
        var props = Object.getOwnPropertyNames(from);
        var dest = this;
        props.forEach(function(name) {
            if (name in dest) {
                var destination = Object.getOwnPropertyDescriptor(from, name);
                Object.defineProperty(dest, name, destination);
            }
        });
        return this;
    }
});


/**
 * Handle the fetching and processing of the content of a bookmark
 *
 */
var BookieContent = function (opts) {
    var defaults = {
        bookieurl: 'http://127,.0.0.1:6543/',
        queue_tube: 'default',
        queue_conn: undefined,
	};

	if (typeof opts === 'object') {
		opts = defaults.extend(opts);
	} else {
		opts = defaults;
	}

    var that = {};
    that.opts = opts;

    that.queue_content = function (hash_id, content) {
        var escaped,
            post_data = JSON.stringify({'hash_id': hash_id, 'content': content}),
            qclient = that.opts.queue_conn;

        try {
            escaped = qs.escape(post_data);

            qclient.put(escaped).
                onSuccess(function(data) {
                    log.info("Added to queue: " + hash_id);
                });
         } catch (err) {
            log.error('escaping url content');
            log.error(err);
            log.error(post_data.substr(0,100));
        }
    };

    /**
     * We can only fetch html and parse content for html pages
     *
     * Exclude images, pdfs
     *
     */
    that.ext_is_valid = function (ext) {
        switch(ext) {
        case '.png':
          return false;
          break;
        case '.jpg':
          return false;
          break;
        case '.gif':
          return false;
          break;
        case '.pdf':
          return false;
          break;
        case '.mp3':
          return false;
          break;
        case '.mp4':
          return false;
          break;
        default:
          return true;
        }
    };

    that.fetch_url = function (hashed) {
        var hash_id = hashed.hash_id,
            someUri = hashed.url,
            ext = someUri.substr(-4);

        if (that.ext_is_valid(ext)) {
            log.info("Fetching content for url: " + someUri);
            var req_data = {'uri': someUri,
                            'encoding': "utf-8",
                            "max_redirs": 10
                },
                req_callback = function (error, body) {
                                   if (error) {
                                       // error is an object with message and
                                       // statusCode we need to send to the
                                       // server to log this
                                       log.error('FETCHING URL');
                                       log.error(inspect(error));
                                   } else {
                                       log.info("Fetched " + someUri + " OK!");
                                       that.queue_content(hash_id, body);
                                   }
                },
                dl = new req(req_data);

            dl.asString(req_callback);
        } else {
            log.info('Skipping non html file: ' + someUri);
        }
    };

    return that;
};


/**
 * Handle API calls to the bookie instance
 *
 */
var BookieAPI = function (opts) {
    var opts,
        defaults = {
            bookieurl: 'http://127,.0.0.1:6543/',
        };

	if (typeof opts === 'object') {
		opts = defaults.extend(opts);
	} else {
		opts = defaults;
	}

    log.info('Using API url: ' + opts.bookieurl);

    var that = {};
    that.opts = opts;

    that.processArray = function(items, process) {
        var todo = items.concat();
        log.info("Processing");

        setTimeout(function() {
            process(todo.shift());
            if(todo.length > 0) {
                setTimeout(arguments.callee, TIMEOUT);
            }
        }, 25);
    };

    that.getReadableList = function() {
        var req_data = {uri: that.opts.bookieurl + '/get_readable',
                        method: "GET"
            },
            req_callback = function (error, body) {
                               if (error) {
                                   log.error('fetching readable list');
                                   log.error(error);
                               }

                               var res = JSON.parse(body);
                               that.processArray(res.payload.urls, function (hashed) {
                                   content = BookieContent({
                                       bookieurl: API,
                                       queue_conn: bean_client
                                   });

                                   content.fetch_url(hashed);
                               });
                           };

        log.info("Requesting list of bookmarks to readable");
        var dl = new req(req_data);
        dl.asString(req_callback);

    };

    return that;

};


// let's get this party started
log.info('Starting up');

var bookie_api = BookieAPI({'bookieurl': API});
bookie_api.getReadableList();
