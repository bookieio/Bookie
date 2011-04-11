test('bookie_init', function () {
    // first set an api key and we'll check it later
    localStorage['api_key'] = 'testingapikey';
    // we need an API url to get past the init since it's checking for it now
    localStorage['api_url'] = '127.0.0.1';
    bookie.init();
    console.log(localStorage['api_key']);
    console.log($('#api_key'));

    equal('testingapikey', $('#api_key').val(),
            "Verify we set the api key in init()");

});


/**
 * Make sure that once we enable the delete button it's visible
 *
 */
test("delete_button", function () {
    equal($('#delete:visible').length, 0,
            "Delete button is not visible");
    bookie.init();
    bookie.ui.enable_delete();
    equal($('#delete:visible').length, 1,
            "Delete button is visible");
});


/**
 * Test the form population
 *
 * Given a tab object with a url/page title
 * We're testing that a call to posts/get works and loads up our form with
 * great data from the database
 *
 */
test('populate_form', function () {

    // let's try mocking out the ajax method
    var options;
    $.ajax = function (params) {
        options = params;
    }

    mocked_return = '<?xml version="1.0" encoding="UTF-8"?>' +
        '<posts user="none" dt="2010-03-10" tag="">' +
            '<post href="http://google.com"' +
            '    hash="---"' +
            '    description="Test Description"' +
            '    extended="Extended Description"' +
            '    tag="unit test" time=""' +
            '    others="--"></post> ' +
        '</posts>';

    var url = {
        'url': 'http://google.com',
        'title': 'Google search stuff'
    };

    bookie.populateFormBase(url);

    // now call the success method since we should get a 200 here
    options.success(mocked_return);

    // now the form should have a tag and description there
    equal('unit test', $('#tags').val(),
            "The tags we mocked should be set on the form");
    equal('Test Description', $('#description').val(),
            "The desc we mocked should be set on the form");
    equal('Extended Description', $('#extended').val(),
            "The ext desc we mocked should be set on the form");

    // and the delete button should not be visible since we found a record
    equal($('#delete:visible').length, 1,
            "Delete button is visible");
});

/**
 * Verify that we get the correct data and ui calls when we store a bookmark
 */
test('saveBookmarkSuccess', function () {
    var logger, mocked_return, options;

    logger = [];
    mocked_return = '<result code="done"></result>';
    parser=new DOMParser();
    mocked_xml=parser.parseFromString(mocked_return,"text/xml");

    // let's try mocking out the ajax method
    $.ajax = function (params) {
        options = params;
    }

    // we also need to mock out the notifications so we can catch them
    bookie.ui.notify = function (code, message) {
        logger.push({"type": "info",
                      "code": 200,
                      "shortText": "Ok",
                      "longText": "saved"
                    })
    }

    bookie.call.saveBookmark({});
    options.success(mocked_xml);

    // now check the logger for the result
    equal(logger[0]['shortText'], "Ok",
        "The notify code of the saveBookmark was 'done'");

});


/**
 * Verify that we get the failed message on a bad call
 */
test('saveBookmarkFail', function () {
    var logger, mocked_return, options;

    logger = [];
    mocked_return = '<result code="Bad Request: missing url" />';
    parser=new DOMParser();
    mocked_xml=parser.parseFromString(mocked_return,"text/xml");

    // let's try mocking out the ajax method
    $.ajax = function (params) {
        options = params;
    }

    // we also need to mock out the notifications so we can catch them
    bookie.ui.notify = function (code, message) {
        logger.push({
                      "type": "error",
                      "code": 400,
                      "shortText": "Err",
                      "longText": "Could not save bookmark"
                    })
    }

    bookie.call.saveBookmark({});
    options.success(mocked_xml);

    // now check the logger for the result
    equal(logger[0]['shortText'], 'Err',
        "The notify code of the saveBookmark was 'Base Request...'");

});
