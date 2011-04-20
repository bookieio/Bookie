//This wrapper is used in bookie-core.js.  I can't tell if it's needed here too.
//window.addEventListener("load", function(event){
    //(function(loader){
        //loader.loadSubScript("chrome://bookie/content/js/jquery.min.js");
    //})(
        //Components.classes["@mozilla.org/moz/jssubscript-loader;1"].getService(
            //Components.interfaces.mozIJSSubScriptLoader
        //)
    //);

    // Trying this doesn't work - but I don't know if it should.  Seems like bookie isn't visible.
    //bookie.aConsoleService.logStringMessage('foo');
    //(function (module, $) {
        // Trying this doesn't work either.
        //module.aConsoleService.logStringMessage('bar');

    //})(bookie || {}, jQuery);

    // This is an attempt to make http://meherranjan.com/blog/a-guide-to-using-jquery-inside-firefox-extension/
    // work (approach 2).  This is used with bookie-core.js NOT included in the .xul file.  It looks like this works ok
    // on its own, but I can't work out how to use the jQuery bit you get back to include useful stuff from
    // bookie-core.js.
    var BookiejQuery = {
        loadjQuery: function(context) {
            var loader = Components.classes["@mozilla.org/moz/jssubscript-loader;1"].getService(Components.interfaces.mozIJSSubScriptLoader);
            loader.loadSubScript("chrome://bookie/content/js/jquery.min.js", context);

            var jQuery = window.jQuery.noConflict(true);
            if(typeof(jQuery.fn._init) == 'undefined') {
                jQuery.fn._init = jQuery.fn.init;
            }
            this.jQuery = jQuery;
        },
    };

    var bookie = (function (module, $) {
        // Just a placeholder for some testing.
    })(bookie || {}, jQuery);

    // Here's some stuff that makes preferences behave in firefox.  Commented out while working on jQuery stuff.
    /*var Bookie = {
        prefs: null,
        serverUrl: "",
        apiKey: "",

        startup: function()
        {
             this.prefs = Components.classes["@mozilla.org/preferences-service;1"]
                 .getService(Components.interfaces.nsIPrefService)
                 .getBranch("bookie.");
             this.prefs.QueryInterface(Components.interfaces.nsIPrefBranch2);
             this.prefs.addObserver("", this, false);

             this.serverUrl = this.prefs.getCharPref("server");
             this.apiKey = this.prefs.getCharPref("apikey");

        },    

        shutdown: function()
        {
            this.prefs.removeObserver("", this);
        },

        observe: function(subject, topic, data)
        {
            if (topic != "nsPref:changed")
            {
                return;
            }
 
            switch(data)
            {
                case "server":
                    this.serverUrl = this.prefs.getCharPref("server");
                    break;
                case "apikey":
                    this.apiKey = this.prefs.getCharPref("apikey");
                    break;
             }
        },

    }

    window.addEventListener("load", function(e) { Bookie.startup(); }, false);
    window.addEventListener("unload", function(e) { Bookie.shutdown(); }, false);*/

//}, false);
