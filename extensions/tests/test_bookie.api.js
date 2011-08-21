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



var API_URL = 'http://dev.bmark.us',
    USERNAME = 'admin',
    API_KEY = 'd05ed874d34b',
    HASH_ID = 'c5c21717c99797',
    FAILED = function (data, status_string) {
        // if we hit this the request failed in a bad way
        console.log(data);
        console.log(status_string);

        ok(false, "Shouldn't have a bad api requests here");
        start();
    };


/**
 * Verify we can fetch real bookmark data from the live dev testing urls
 *
 */
test('live.bookmark', function () {
    // we're going to test both with and without content so two calls
    expect(2);

    console.log('bookmark');
    stop();
    bookie.api.init(API_URL, USERNAME, API_KEY);

    bookie.api.bookmark(HASH_ID, {}, {
                        'success': function (data) {
                            var bmark = data.bmark
                            ok(bmark.hash_id == HASH_ID,
                                "The right bookmark came down by hash_id");
                            ok(!bmark.readable,
                                "Should not have readable by default");
                            start();

                        },
                        'error': FAILED
    });
});

/**
 * Test we get readable content
 *
 */
test('live.bookmark_readable', function () {
    // we're going to test both with and without content so two calls
    expect(2);

    stop();
    bookie.api.init(API_URL, USERNAME, API_KEY);

    console.log('readable');

    bookie.api.bookmark(HASH_ID, {
                        'get_last': false,
                        'with_content': true,
                    },
                    {
                        'success': function (data) {
                            var bmark = data.bmark
                            ok(bmark.hash_id == HASH_ID,
                                "The right bookmark came down by hash_id");
                            ok(bmark.readable,
                                "Should have readable content");
                            start();

                        },
                        'error': FAILED
                    });
});


/**
 * Recent list
 *
 */
test('live.recent', function () {
    expect(3)

    stop();
    bookie.api.init(API_URL, USERNAME, API_KEY);

    console.log('recent');

    bookie.api.recent({
                'count': 10,
                'page': 0,
            },
            {
                'success': function (data) {
                    ok(data.count == 10,
                        "We need to get 10 bookmarks");
                    ok(data.bmarks[0].hash_id !== undefined,
                        "Should have readable content");
                    ok(data.bmarks[0].readable === undefined,
                        "Should not have content by default");

                    start();

                },
                'error': FAILED
            });
});


/**
 * Popular url tets
 *
 */
test('live.popular', function () {
    expect(3)

    stop();
    bookie.api.init(API_URL, USERNAME, API_KEY);

    console.log('popular');

    bookie.api.popular({
                'count': 5,
                'page': 0,
            },
            {
                'success': function (data) {
                    ok(data.count == 5,
                        "We need to get 5 bookmarks");
                    ok(data.bmarks[0].hash_id !== undefined,
                        "Should have readable content");
                    ok(data.bmarks[0].readable === undefined,
                        "Should not have content by default");

                    start();

                },
                'error': FAILED
            });
});


var TEST_BMARK = {
        'url': 'https://github.com/mitechie/Bookie',
        'tags': 'git github bookie',
        'description': 'js api test',
        'extended': 'longer js api test',
        'fulltext': '<div class="main">Main body text for fulltext</div>'
    },
    TEST_HASH = '110e3adbf8110c';


/**
 * Add bookmark
 *
 */
test('live.add', function () {
    expect(3)

    stop();
    bookie.api.init(API_URL, USERNAME, API_KEY);

    bookie.api.add(TEST_BMARK, {
        'success': function (data) {
            console.log(data);
            ok(data.bmark !== undefined,

                "We should have a bookmark returned");
            ok(data.bmark.hash_id == TEST_HASH,
                "We should have the correct hash id: " + data.bmark.hash_id);
            ok(data.location == _.sprintf("%s/bmark/readable/%s",
                                    API_URL,
                                    TEST_HASH),
                                    "We should have a location that's correct: " + data.location);
            start();
        },
        'error': FAILED
    });
});




/**
 * Remove bookmark
 *
 * This is hackish I know, we're going to delete the bookmark we added in the
 * test for add, if it fails, well it's probably because add failed.
 *
 */
// test('live.popular', function () {
//     expect(3)
// 
//     stop();
//     bookie.api.init(API_URL, USERNAME, API_KEY);
// 
//     bookie.api.popular({
//                 'count': 5,
//                 'page': 0,
//             },
//             {
//                 'success': function (data) {
//                     ok(data.count == 5,
//                         "We need to get 5 bookmarks");
//                     ok(data.bmarks[0].hash_id !== undefined,
//                         "Should have readable content");
//                     ok(data.bmarks[0].readable === undefined,
//                         "Should not have content by default");
// 
//                     start();
// 
//                 },
//                 'error': FAILED
//             });
// });
