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


var ResponseData = function (hashed) {
    var that = {};
    that.hash_id = hashed.hash_id;
    that.url = hashed.url;
    that.content = undefined;
    that.success = true;
    that.status_code = undefined;
    that.status_message = undefined;
    return that;
};

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
            post_data = JSON.stringify({'success': true, 'hash_id': hash_id, 'content': content}),
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
            log.error(post_data.substr(0,50));
        }
    };

    /**
     * If there's a problem parsing, fetching, or otherwise with this url
     * Queue up that we'd like to store a failed fetch so that we don't
     * reprocess for now
     *
     */
    that.queue_error = function (resp) {
        var escaped,
            data = {
                    'success': false,
                    'hash_id': resp.hash_id,
                    'content_type': resp.content_type,
                    'status_code': resp.status_code,
                    'status_message': resp.status_message
            },
            post_data = JSON.stringify(data),
            qclient = that.opts.queue_conn;

        try {
            escaped = qs.escape(post_data);

            qclient.put(escaped).
                onSuccess(function(data) {
                    log.info("Added to error queue: " + data.hash_id);
                });
         } catch (err) {
            log.error('escaping error url content');
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
    that.ext_is_valid = function (ext, resp_data) {
        switch(ext) {
            case '.png':
            case '.jpg':
            case '.gif':
              resp_data.success = false;
              resp_data.content_type = 'image/' + ext.substr(1);
              resp_data.status_code = 1;
              resp_data.status_message = 'url skipped';
              break;
            case '.mp3':
              resp_data.success = false;
              resp_data.content_type = 'audio/' + ext.substr(1);
              resp_data.status_code = 1;
              resp_data.status_message = 'url skipped';
              break;
            case '.mp4':
            case '.mpg':
            case '.mov':
            case '.wmv':
              resp_data.success = false;
              resp_data.content_type = 'video/' + ext.substr(1);
              resp_data.status_code = 1;
              resp_data.status_message = 'url skipped';
              break;
            case '.pdf':
              resp_data.success = false;
              resp_data.content_type = 'application/' + ext.substr(1);
              resp_data.status_code = 1;
              resp_data.status_message = 'url skipped';
              break;
            default:
              // all is well
              break;
        }

        return resp_data;
    };

    that.fetch_url = function (hashed) {
        var hash_id = hashed.hash_id,
            someUri = hashed.url,
            ext = someUri.substr(-4),
            resp = that.ext_is_valid(ext, hashed);

        if (resp.success) {
            log.info("Fetching content for url: " + someUri);
            var req_data = {'uri': someUri,
                            "max_redirs": 10
                },
                req_callback = function (error, body) {
                                   if (error) {
                                       log.info('FOUND ERROR');
                                       resp.success = false;
                                       resp.status_code = error.statusCode;
                                       resp.status_message = error.message;

                                       // if we got here assume it was html
                                       // content type
                                       resp.content_type = 'text/html';
                                       that.queue_error(resp);

                                   } else {
                                       log.info("Fetched " + someUri + " OK!");
                                       resp.sucess = true;
                                       that.queue_content(hash_id, body);
                                   }
                },
                dl = new req(req_data);

            dl.asString(req_callback);
        } else {
            // then we skipped this because it was an image/binary send to
            // queue to store result
            log.info('Skipping non html file: ' + someUri);
            that.queue_error(resp);
        }
    };

    return that;
};


/**
 * Handle API calls to the bookie instance
 *
 */
var BookieAPI = function (opts) {
    var defaults = {
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
            process(ResponseData(todo.shift()));
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
                                   log.info(inspect(hashed));
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
