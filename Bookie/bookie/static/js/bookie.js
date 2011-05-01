/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

var bookie = (function ($b, $) {

    // bootstrap some custom things that the extensions will jump in on
    $b.ui = {};
    $b.call = {};

    // some constants we'll use throughout
    // dom hook for triggering/catching events fired
    $b.EVENTID = 'body';

    /**
     * Define events supported
     *
     */
    $b.events = {
        'LOAD': 'load',
        'TAG_FILTER': 'tag_filter',
        'SEARCH': 'search'
    };

    /**
     * Once the page is loaded, perform some nice basics we need
     *
     */
    $b.load = function (ev) {
        console.log('loading');

        // init the tag filter ui completion code
        $($b.EVENTID).trigger($b.events.TAG_FILTER);
    };


    /*
     * fetch a set of completion options
     * Used for completing tag names in the extension
     *
    */
    $b.call.tagComplete = function (substring, callback) {
        var opts = {
            url: "/delapi/tags/complete",
            type: "GET",
            dataType: "xml",
            data: {
                tag: substring
            },

            success: function (xml) {
                console.log('success call to complete');
                tag_list = [];
                results = $(xml).find("tag");
                results.map(function () {
                    tag_list.push($(this).text());
                });

                callback(tag_list);
            }
        };

        $.ajax(opts);
    };


    /**
     * perform an ajax search based on the terms passed in
     *
     * Performing an AJAX request with a standard response model
     *   - success
     *   - message
     *   - payload
     *       - html
     *
     */
    $b.call.search = function (ev, terms) {
        var one_term, opts;
        console.log('terms');
        console.log(terms);

        console.log('calling search');
        console.log(terms);

        one_term = terms.join("/");
        opts = {
            url: "/search/" + one_term,
            type: "GET",
            dataType: "json",
            success: function (data) {
                // replace the body of the page with the content that came back
                if (data.success) {
                    $('.data_body').html(data.payload.html);
                }
            }
        };

        $.ajax(opts);
    };


    /**
     * Control the tag filter ui on the main pages
     *
     */
    $b.ui.init_tag_filter = function (ev) {
        console.log('triggering tag filter');
        var tags = [];
        $(function() {

            function split(val) {
                // split on spaces
                return val.split(/ /);
            };

            /**
              * Pull the search term characters from the end of the
              * text input
              *
             */
            function extractLast(term) {
                return split(term).pop();
            }

            $("#tag_filter").bind( "keydown", function( event ) {
                    // don't navigate away from the field on tab when selecting an item
                    if ( event.keyCode === $.ui.keyCode.TAB &&
                            $( this ).data( "autocomplete" ).menu.active ) {
                        event.preventDefault();
                    }
                }).autocomplete({
                    source: function (request, response) {
                        bookie.call.tagComplete(extractLast(request.term), response);
                    },
                    search: function() {
                        // custom minLength
                        var term = extractLast(this.value);
                        console.log('term');
                        console.log(term);
                        if ( term.length < 1 ) {
                            return false;
                        }
                    },
                    focus: function() {
                        // prevent value inserted on focus
                        return false;
                    },
                    select: function(event, ui) {
                        console.log(this.value);
                        var terms = split(this.value);
                        // remove the current input
                        terms.pop();
                        // add the selected item
                        terms.push(ui.item.value);
                        // add placeholder to get the comma-and-space at the end
                        terms.push("");
                        this.value = terms.join(" ");

                        $($b.EVENTID).trigger($b.events.SEARCH, [terms]);
                        return false;
                    }
                });
        });
    };


    // only need to call init on the page read event
    $b.init = function () {
        // make sure we bind the page load event
        $($b.EVENTID).bind($b.events.LOAD, $b.load);

        // bind some other events we might want read to go out of the gates
        $($b.EVENTID).bind($b.events.TAG_FILTER, $b.ui.init_tag_filter);
        $($b.EVENTID).bind($b.events.SEARCH, $b.call.search);


        // now trigger the load since we're ready to go from here
        $($b.EVENTID).trigger($b.events.LOAD);
    };

    return $b;
})(bookie || {}, jQuery);
