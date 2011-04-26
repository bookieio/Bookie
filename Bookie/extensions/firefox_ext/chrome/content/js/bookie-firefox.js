// This is an attempt to make http://meherranjan.com/blog/a-guide-to-using-jquery-inside-firefox-extension/
// work (approach 2).  This is used with bookie-core.js NOT included in the .xul file.  It looks like this works ok
// on its own, but I can't work out how to use the jQuery bit you get back to include useful stuff from
// bookie-core.js.

var loader, jq_var, bookie;

loader = Components.classes["@mozilla.org/moz/jssubscript-loader;1"].getService(Components.interfaces.mozIJSSubScriptLoader);
loader.loadSubScript("chrome://bookie/content/js/jquery.min.js");
loader.loadSubScript("chrome://bookie/content/js/bookie-core.js");
jq_var = jQuery.noConflict(true);

bookie = (function(module, $, console) {
    var setup_prefs;

    setup_prefs = function () {
        module.prefs = Components.classes["@mozilla.org/preferences-service;1"]
            .getService(Components.interfaces.nsIPrefService)
            .getBranch("bookie.");
        module.prefs.QueryInterface(Components.interfaces.nsIPrefBranch2);
        module.prefs.addObserver("", module, false);

        // CORE CONFLICT; definition of api_key
        module.api_url = module.prefs.getCharPref("server");
        module.api_key = module.prefs.getCharPref("apikey");
    }

    module.popup = function() {
        // shared populate form
        console.log('in popup pre init');

        module.init();

        // @todo see if tihs is necessary, make a FF specific init function
        module.$('#api_key').val(module.api_key);
        module.$('#tags').val('');

        // focus to the tags field since we normally have the title already and
        // that's next
        module.$('#tags').focus();

        module.call.getBookmark(url, function(xml) {
            var result, code, found;

            result = module.$(xml).find("result");
            found = module.$(xml).find("post");

            found.map(function () {
                // add the tags to the tag ui
                module.$('#tags').val(module.$(this).attr('tag'));

                // add the description to the ui
                module.$('#description').val(module.$(this).attr('description'));

                // add the notes to the ui
                $('#extended').val(module.$(this).attr('extended'));

                // now enable the delete button in case we want to delete it
                module.ui.enable_delete();

                module.$('#bookie-delete').attr('disabled', 'false');

                module.$('#bookie-delete').click(function(ev) {
                    module.$('#bookie-delete').attr('disabled', 'true');
                    module.$('#bookie-panel').get(0).hidePopup();
                    module.call.removeBookmark(url, module.api_key);
                });

            });
        });

    };

    module.submit = function(ev) {
        var formData = {
            url: module.$('#url').val(),
            tags: module.$('#tags').val(),
            api_key: module.$('#api_key').val(),
            description: module.$('#description').val(),
        };
        module.ffSaveBookmark(module.$.param(formData));
        module.$('#bookie-panel').get(0).hidePopup();
    };

    // module.ffSaveBookmark = function (params) {
    //     var opts;

    //     opts = {
    //         url: module.api_url + "/delapi/posts/add",
    //         data: params,
    //         success: function(xml) {
    //             var result, code;
    //             result = module.$(xml).find("result");

    //             code = result.attr("code");

    //             if (code == "done") {
    //                 module.consoleService.logStringMessage('OK');
    //             } else {
    //                 // need to notify that it failed
    //                 module.consoleService.logStringMessage('Failed' + params);
    //             }
    //         },
    //     };

    //     request(opts);
    // };

    // function request(options) {
    //     var defaults, opts;

    //     defaults = {
    //         type: "GET",
    //         dataType: "xml",
    //         error: function(jqxhr, textStatus, errorThrown) {
    //             module.consoleService.logStringMessage('ERROR: ' + module.response_codes[jqxhr.status] + ' ' +
    //                 textStatus);
    //         }
    //     };

    //     opts = module.$.extend({}, defaults, options);
    //     module.$.ajax(opts);
    // };

    // module.observe = function(subject, topic, data) {
    //     if (topic != "nsPref:changed") {
    //         return;
    //     }

    //     switch(data) {
    //         case "server":
    //             module.api_url = module.prefs.getCharPref("server");
    //             break;
    //         case "apikey":
    //             module.api_key = module.prefs.getCharPref("apikey");
    //             break;
    //      }
    // };

    // module.shutdown = function() {
    //     module.prefs.removeObserver("", module);
    // };

    module.ff_init = (function(context) {
        console.log('Adding to bookie in bookie-firefox');

        // we use prefs vs localStorage
        setup_prefs();

        // bind the FF specific button
        $('#bookie-button').bind('click', module.popup);
    });

    return module;

})(bookie || {}, jq_var, console);
