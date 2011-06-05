// helper we'll use over and over in tests
var TEST_HASH = 'd7148c0445ff22',
    API_URL = '127.0.0.1:6543';


$.mockjax({
    url: API_URL + '/api/v1/bmarks/' + TEST_HASH,
    responseTime: 0,
    responseText: {
        "message": "",
        "payload": {
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
        },
        "success": true
    }
});


$.mockjax({
    url: API_URL + '/api/v1/bmarks/blah',
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
    bookie.api.init(API_URL);
    bookie.api.bookmark(TEST_HASH,
        {
            success: function (data) {
                equal(data.payload.bmark.hash_id, TEST_HASH,
                    "The test hash should equal the one from the server");
                start();
            }
        });
});


test('bookie.api.bookmark_bad', function () {
    expect(1);

    stop();
    bookie.api.init(API_URL);
    bookie.api.bookmark('blah',
        {
            success: function (data) {
                equal(data.success, false,
                    "The success should be false");
                start();
            }
        });
});

