// helper we'll use over and over in tests
var GOOGLE_HASH = 'aa2239c17609b2';


test('bookie.utils.hash_url', function () {
    equal(GOOGLE_HASH, bookie.utils.hash_url("http://google.com"),
        "our google hash url should match");
    equal('c5c21717c99797', bookie.utils.hash_url("http://bmark.us"),
        "our bmark.us hash url should match");
});


test('bookie.utils.hash_url', function () {
    var url = "http://google.com";

    // first make sure we don't have the thing in the localStorage
    localStorage.clear();

    equal(false, bookie.utils.is_bookmarked(url),
        "The bookmark should start out not bookmarked");
    localStorage.setItem(GOOGLE_HASH, true);
    equal(true, bookie.utils.is_bookmarked(url),
        "The bookmark should then be bookmarked");
});

