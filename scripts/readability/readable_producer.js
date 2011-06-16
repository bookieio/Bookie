// var bs = require('node_modules/nodestalker/lib/beanstalk_client.js');
var bs = require('nodestalker');
var request = require('request'),
    url = require('url'),
    http = require('http'),
    qs = require('querystring');

var client = bs.Client();
var API = "http://127.0.0.1:6543/api/v1/bmarks",
    TIMEOUT = 500;

function queue_content(hash_id, content) {
    var escaped,
        post_data = JSON.stringify({'hash_id': hash_id, 'content': content});

    try {
        escaped = qs.escape(post_data);
    } catch (err) {
        console.error(err);
        console.error(post_data)
    }

    client.use('default').onSuccess(function(data) {
      client.put(qs.escape(post_data) + "\r\n").onSuccess(function(data) {
          console.log("Added to queue: " + hash_id);
          console.log(data);
          // client.disconnect();
      });
    });
}

function processArray(items, process) {
    var todo = items.concat();
    console.log("Processing");

    setTimeout(function() {
        process(todo.shift(), queue_content);
        if(todo.length > 0) {
            setTimeout(arguments.callee, TIMEOUT);
        }
    }, 25);
}

function getPage (hashed, callback) {
      var hash_id = hashed.hash_id,
          someUri = hashed.url;

      var end = someUri.substr(-4);
      if(end != '.png' && end != ".jpg" && end != ".gif") {
          var req_data = {'uri': someUri, 'encoding': "utf-8", "maxSockets": 5},
              req_callback = function (error, response, body) {
                                 console.log("Fetched " + someUri + " OK!");
                                 callback(hash_id, body);
                             };

          request(req_data, req_callback);
      }
}


function getReadableList() {
    var req_data = {uri: API + '/get_readable', method: "GET"},
        req_callback = function (error, response, body) {
                           var res = JSON.parse(body);
                           processArray(res.payload.urls, getPage);
                       };

    request(req_data, req_callback);
}


// let's get this party started
console.log('starting to get the list');
getReadableList();
