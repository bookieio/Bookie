test('bookie_init', function () {
    // first set an api key and we'll check it later
    localStorage['api_key'] = 'testingapikey';
    console.log('init');
    bookie.init();
    equal('testingapikey', $('#api_key').val(), "Verify we set the api key in init()");

});


/**
 * Make sure that once we enable the delete button it's visible
 *
 */
test("delete_button", function() {
    equal($('#delete:visible').length, 0, "Delete button is not visible");
    bookie.init();
    bookie.ui.enable_delete();
    equal($('#delete:visible').length, 1, "Delete button is visible");
});
