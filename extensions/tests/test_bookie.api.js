// helper we'll use over and over in tests
var TEST_HASH = 'd7148c0445ff22',
    FAKE_URL = '127.0.0.1:6543',
    USERNAME = 'admin',
    API_KEY = 'test';


$.mockjax({
    url: _.sprintf("%s/api/v1/%s/bmark/%s", FAKE_URL, USERNAME, TEST_HASH),
    responseTime: 0,
    responseText: {
            "bmark": {
                "updated": "2011-06-04 21:21:40",
                "extended": "",
                "description": "s3cp.py \u2014 Gist",
                "tags": [{"tid": 7289, "name": "!toread"}],
                "bid": 16715,
                "readable": {"content": "content"},
                "stored": "2011-06-01 21:49:57",
                "tag_str": null,
                "clicks": 3,
                "hash_id": "d7148c0445ff22"
            }
    }
});


$.mockjax({
    url: _.sprintf("%s/api/v1/%s/bmark/blah", FAKE_URL, USERNAME),
    responseTime: 0,
    responseText: {
        "message": "Bookmark for hash id blah not found",
        "payload": {},
        "success": false
    }
});


test('bookie.api.bookmark', function () {
    expect(1);

    stop();
    bookie.api.init(FAKE_URL, USERNAME, API_KEY);
    bookie.api.bookmark(TEST_HASH,
        {
            success: function (data) {
                equal(data.bmark.hash_id, TEST_HASH,
                    "The test hash should equal the one from the server");
                start();
            },
            error: function (data, status_string) {
                ok(false, "The bookmark failed with error code " + status_string);
            }
        });
});


test('bookie.api.bookmark_bad', function () {
    expect(1);

    stop();
    bookie.api.init(FAKE_URL);
    bookie.api.bookmark('blah',
        {
            success: function (data) {

            },
            error: function (data, status_string) {
                equal(status_string, 'error',
                    "The bmark should be 404 error");
                start();

            },
        });
});


// var API_URL = 'http://dev.bmark.us',
//     USERNAME = 'admin',
//     API_KEY = 'd05ed874d34b',
//     HASH_ID = 'c5c21717c99797',
//     FAILED = function (data, status_string) {
//         // if we hit this the request failed in a bad way
//         console.log(data);
//         console.log(status_string);
//         
//         ok(false, "Shouldn't have a bad api requests here");
//         start();
//     };
// 
// 
// /**
//  * Verify we can fetch real bookmark data from the live dev testing urls
//  *
//  */
// test('bookie.api.live_bookmark', function () {
//     // we're going to test both with and without content so two calls
//     expect(2);
// 
//     stop();
//     bookie.api.init(API_URL, USERNAME, API_KEY);
// 
//     bookie.api.bookmark(HASH_ID, {
//                         'success': function (data) {
//                             ok(data.hash_id == HASH_ID,
//                                 "The right bookmark came down by hash_id");
//                             ok(!data.readable,
//                                 "Should not have readable by default");
//                             start();
// 
//                         },
//                         'error': FAILED
//     });
// });
