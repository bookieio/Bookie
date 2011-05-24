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
        'RECENT': 'recent',
        'POPULAR': 'popular',
        'SEARCH': 'search',
        'NEXT_PAGE': 'next',
        'PREV_PAGE': 'prev',
        'VIEW': 'view'
    };


    $b.request = function (options) {
        var defaults, opts;

        defaults = {
            type: "GET",
            dataType: "json",
            context: $b,
            timeout: 30000,
            error: function(jqxhr, textStatus, errorThrown) {
                console.log('REQUEST_ERROR');
                console.log('Response Code: ' + jqxhr.status);
                console.log('Response Status: ' + textStatus);
                console.log(jqxhr);
            }
        };

        options.url = APP_URL + options.url;

        opts = $.extend({}, defaults, options);
        $.ajax(opts);
    };


    $b.page = {
        'url': '',
        'page': 0,
        'count': 10,
        'func': "",             // used for what type of thing are we looking at, load_recent
        'terms': [],
        'query_params': "",
        'clear': function () {
            $b.page.url = "";
            $b.page.page = 0;
            $b.page.count = 10;
            $b.page.terms = [];
            $b.page.query_params = "";
        },
        'generate_url': function () {
            url_str = ["count=" + this.count,
                       "page=" + this.page,
                      ].join('&');
            return url_str;
        }
    };


    /**
     * Once the page is loaded, perform some nice basics we need
     *
     */
    $b.load = function (ev) {
    };


    $b.load_recent = function (ev, extra_params) {
        // we need to get the list of recent from the api
        var url, opts;
        $b.page.url = "/api/v1/bmarks/recent?" + $b.page.generate_url();
        $b.page.func = $b.events.RECENT;

        data_home = extra_params.data_home;

        var opts = {
            url: $b.page.url,
            success: function (data) {
                if (data.success == true) {
                    var page = data.payload.page;
                    $b.page.page = page;
                    $b.ui.results.update(data.payload.bmarks, 'Recent: Page ' + page, data_home);
                } else {
                    console.error('ERROR getting recent');
                }

                $.mobile.pageLoading(true);
            },
            'complete': function () {
                if (data_home != '#home_recent') {
                    $.mobile.changePage('#results', 'slide', back=false, changeHash=false);
                }

                $.mobile.pageLoading(true);
            }

        };

        $.mobile.pageLoading();
        $b.request(opts);

        // don't do what the click says yet
        ev.preventDefault();
    };


    $b.load_popular = function (ev, extra_params) {
        // we need to get the list of popular from the api
        var url, opts;
        $b.page.url = "/api/v1/bmarks/popular?" + $b.page.generate_url();
        $b.page.func = $b.events.POPULAR;

        data_home = extra_params.data_home;

        opts = {
            url: $b.page.url,
            success: function (data) {
                if (data.success == true) {
                    var page = data.payload.page;
                    $b.page.page = page;
                    $b.ui.results.update(data.payload.bmarks, 'Popular: Page ' + page, data_home);
                } else {
                    console.error('ERROR getting popular');
                }

                $.mobile.pageLoading(true);
            },
            'complete': function () {
                $.mobile.changePage('#results', 'slide', back=false, changeHash=false);
                $.mobile.pageLoading(true);
            }

        };

        $.mobile.pageLoading();
        $b.request(opts);

        // don't do what the click says yet
        ev.preventDefault();
    };


    /**
     * Handle the event to load a bookmark
     * extra_params:
     *     - hash_id
     *
     */
    $b.load_bookmark = function (ev, extra_params) {
        var url, opts;
        $b.page.url = "/api/v1/bmarks/" + extra_params.hash_id;
        $b.page.func = $b.events.VIEW;

        opts = {
            url: $b.page.url,
            success: function (data) {
                if (data.success == true) {
                    var bmark = data.payload.bmark;
                    $view = $('#view_content');

                    $view.html("");

                    // let's pretty up a date for diplay
                    pretty_date = new Date(bmark.stored);
                    bmark['pretty_date'] = pretty_date;

                    $("#view_template").tmpl([bmark]).prependTo($view)

                } else {
                    console.error('ERROR getting bookmark');
                }

            },
            'complete': function () {
                $.mobile.changePage('#view', 'slide', back=false, changeHash=true);
                $.mobile.pageLoading(true);
            }

        };

        $.mobile.pageLoading();
        $b.request(opts);

        // don't do what the click says yet
        ev.preventDefault();
    };


    $b.search = function (ev, extra_params) {
        // search for a url given the search content
        var url, opts, terms, with_content, data_home;

        terms = extra_params.terms;
        with_content = extra_params.with_content;

        // if the terms are undefined, check if we have any from a previous
        // page call
        if (terms == undefined) {
            terms = $b.page.terms;
        } else {
            $b.page.terms = terms;
        }

        if (with_content == undefined) {
            with_content = $b.page.query_params;
        } else if (with_content == "true") {
            $b.page.query_params = "&content=" + extra_params.with_content;
        }

        // the id of the <ul> we're sticking results into
        // (home page vs results page)
        data_home = extra_params.data_home;

        $b.page.url = "/api/v1/bmarks/search/" + terms.join('/');
        $b.page.url = $b.page.url + "?" + $b.page.generate_url() + $b.page.query_params;
        $b.page.func = $b.events.SEARCH;

        var opts = {
            url: $b.page.url,
            success: function (data) {
                if (data.success == true) {
                    var page = data.payload.page,
                        page_title = "Search: " + data.payload.phrase;


                    if ($b.page.query_params != "") {
                        page_title = page_title + "<br /> (searching cached content)"
                    }

                    $b.page.page = page

                    $b.ui.results.update(data.payload.search_results,
                                         page_title,
                                         data_home)
                } else {
                    console.error('ERROR getting search');
                }
            },
            'complete': function () {
                $.mobile.changePage('#results', 'slide', back=false, changeHash=false);
                $.mobile.pageLoading(true);
            }
        };

        $.mobile.pageLoading();
        $b.request(opts);

        // don't do what the click says yet
        ev.preventDefault();
    };


    /**
     * We want to manage all aspects of the results page content
     *
     */
    $b.ui.results = {
        'tpl_id': '#resultLink',
        'title_id': '#results_title',
        'update': function (data, title, data_home) {
            var page = $b.page.page;
            $(data_home).html("");
            // $(data_home).listview();

            console.log('Updating ' + data_home);
            $("#resultLink").tmpl(data).prependTo(data_home);
            $($b.ui.results.title_id).html(title);

            // this isn't always init'd so need to init it first
            $(data_home).listview('refresh');

            // now bind the swipe event to allow following of the links
            $('.bookmark_link').bind('click', function (ev) {
                // the url we need to call is /redirect/hash_id
                var hash_id = $(this).attr('data-hash'),
                    url = APP_URL + "/redirect/" + hash_id;

                var newwindow = window.open(url, '_blank');
                newwindow.focus();
                return false;
                ev.preventdefault();
            });

            // now bind the gear icon to view this bookmark in detail
            $('.bookmark_view').bind('click', function (ev) {
                var hash_id = $(this).attr('data-hash');
                ev.preventDefault();

                $($b.EVENTID).trigger($b.events.VIEW, {'hash_id': hash_id});
            });
        }
    };


    // only need to call init on the page read event
    $b.init = function () {

        $($b.EVENTID).bind($b.events.RECENT, $b.load_recent);
        $('.go_recent').bind('click', function (ev) {
            ev.preventDefault();

            $b.page.clear();
            $($b.EVENTID).trigger($b.events.RECENT, {data_home: '#results_list'});
            $('.go_recent').addClass('ui-btn-active ui-state-persist');
            $('.go_popular').removeClass('ui-btn-active ui-state-persist');
            $('.go_search').removeClass('ui-btn-active ui-state-persist');
        });

        $($b.EVENTID).bind($b.events.POPULAR, $b.load_popular);
        $('.go_popular').bind('click', function (ev) {
            ev.preventDefault();

            $b.page.clear();
            $($b.EVENTID).trigger($b.events.POPULAR, {data_home: '#results_list'});
            $('.go_popular').addClass('ui-btn-active ui-state-persist');
            $('.go_recent').removeClass('ui-btn-active ui-state-persist');
            $('.go_search').removeClass('ui-btn-active ui-state-persist');
        });

        $('.go_search').bind('click', function (ev) {
            $b.page.clear();
            $('.go_search').addClass('ui-btn-active ui-state-persist');
            $('.go_popular').removeClass('ui-btn-active ui-state-persist');
            $('.go_recent').removeClass('ui-btn-active ui-state-persist');

        });

        $('#results_previous').bind('click', function (ev) {
            $b.page.page = $b.page.page - 1;
            $($b.EVENTID).trigger($b.page.func, {data_home: '#results_list'});
        });

        $('#results_next').bind('click', function (ev) {
            $b.page.page = $b.page.page + 1;
            $($b.EVENTID).trigger($b.page.func, {data_home: '#results_list'});
        });

        $($b.EVENTID).bind($b.events.SEARCH, $b.search);
        $('.search_form').bind('submit', function (ev) {
            var my_form_id, input_id, terms, with_content;
            console.log('triggered search');

            ev.preventDefault();

            // clear any previous search info
            $b.page.clear();

            // the terms need to be pulled from the search box
            my_form_id = $(this).attr('id');
            input_id = "#" + my_form_id + " input";

            // if this is the main search form, then check with_content
            with_content = false;

            if (my_form_id == 'search_page') {
                with_content = $("#cache_content").val();
                console.log('content');
                console.log(with_content);
            }

            terms = $(input_id).val().split(" ");
            $($b.EVENTID).trigger($b.events.SEARCH, {terms: terms,
                                                     with_content: with_content,
                                                     data_home: '#results_list'});
        });

        $($b.EVENTID).bind($b.events.LOAD, function (ev) {
            $b.page.count = 5;
            $('.listview').listview();
            $($b.EVENTID).trigger($b.events.RECENT, {data_home: '#home_recent'});
        });

        $($b.EVENTID).bind($b.events.VIEW, $b.load_bookmark);
    };

    return $b;
})(bookie || {}, jQuery);
