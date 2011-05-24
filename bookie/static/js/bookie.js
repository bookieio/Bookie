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

        // if we're on the readable page, make sure we catch all links and
        // check if we should follow or not
        $('#readable_content a').bind('click', function (ev) {
            // grab the href value and check if it starts with http or www
            var url = $(this).attr('href'),
                original_url = "";

            if (!_.startsWith(url, 'http') && !_.startsWith(url, 'www')) {
                // instead of this url, open the original web page instead of a
                // broken look into htt://bookie/blah.html
                ev.preventDefault();
                var original_url = $('.bmark').attr('href'),
                    newwindow = window.open(original_url, '_blank');

                newwindow.focus();
                return false;

            } else {
                // this will go well, just keep going and open the link
                return true;
            }
        });
    };


    /*
     * fetch a set of completion options
     * Used for completing tag names in the extension
     *
    */
    $b.call.tagComplete = function (substring, current_terms, callback) {
        var opts = {
            url: "/delapi/tags/complete",
            type: "GET",
            dataType: "xml",
            data: {
                tag: substring,
                current: current_terms.join(" ")
            },

            success: function (xml) {
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
     * Control the tag filter ui on the main pages
     *
     */
    $b.ui.init_tag_filter = function (ev) {
        console.log('triggering tag filter');

        var $tag_filter = $('#tag_filter');

        $tag_filter.superblyTagField({
            complete: function (value, callback) {
                var current_vals, current;

                current_vals = $('#tag_filter').val().split(" ");
                if (current_vals.length === 0) {
                    current = [];
                } else {
                    current = current_vals;
                }

                console.log(current);
                bookie.call.tagComplete(value, current, callback);
            },
        });

        // fire off for existing tags
        // but only if we have a tag to pretty up
        console.log($tag_filter.val());
        if ($tag_filter.val()) {
            $('#tag_filter').change();
        }

        $('form#filter_form').bind('submit', function (ev) {
            ev.preventDefault();
            terms = $('#tag_filter').val().split(" ");
            url = "/recent/" + terms.join('/');
            window.location = url;
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
