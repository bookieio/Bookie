// helper we'll use over and over in tests
var TEST_HASH = 'd7148c0445ff22',
    API_URL = '127.0.0.1:6543',
    USERNAME = 'admin',
    API_KEY = 'test';


    console.log(_.sprintf("%s/api/v1/%s/bmark/%s", API_URL, USERNAME, TEST_HASH))
$.mockjax({
    url: _.sprintf("%s/api/v1/%s/bmark/%s", API_URL, USERNAME, TEST_HASH),
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
    url: _.sprintf("%s/api/v1/%s/bmark/blah", API_URL, USERNAME),
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
    bookie.api.init(API_URL, USERNAME, API_KEY);
    bookie.api.bookmark(TEST_HASH,
        {
            success: function (data) {
                equal(data.bmark.hash_id, TEST_HASH,
                    "The test hash should equal the one from the server");
                start();
            },
            error: function (data, status_string) {
                console.log(data);
                console.log(status_string);
                ok(false, "The bookmark failed with error code " + status_string);
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

            },
            error: function (data, status_string) {
                equal(status_string, 'error',
                    "The bmark should be 404 error");
                start();

            },
        });
});

