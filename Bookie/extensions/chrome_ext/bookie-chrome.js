/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

/* chrome-extension-specific bookie functionality */

var bookie = (function(module, $) {

    module.init = function(form) {
        console.log("Test");
        form.bind('submit', function(ev) {
            var data = form.serialize();
            bookie.saveBookmark(data);
        });
        populateForm();
    }

    function populateForm() {
        chrome.tabs.getSelected(null, function (tab) {
            var url; 

            $('#url').val(tab.url);
            $('#description').val(tab.title);
            $('#api_key').val(localStorage['api_key']);

            url = $('#url').attr('value');
            bookie.getBookmark(url, function(xml) {
                $(xml).find("post").map(function() {
                    // add the tags to the tag ui
                    $('#tags').val($(this).attr('tag'));

                    // add the description to the ui
                    $('#description').val($(this).attr('description'));

                    // add the description to the ui
                    $('#extended').text($(this).attr('extended'));
                });
            });
        });
    }
    return module;
})(bookie || {}, jQuery);
