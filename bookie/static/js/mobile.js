/*jslint eqeqeq: false, browser: true, debug: true, onevar: true, plusplus: false, newcap: false, */
/*global $: false, window: false, self: false, escape: false, mor: false, sprintf: false, chrome: false, localStorage: false, */

var bookie = (function ($b, $) {

    // bootstrap some custom things that the extensions will jump in on
    $b.ui = {};
    $b.call = {};

    // some constants we'll use throughout
    // dom hook for triggering/catching events fired
    $b.EVENTID = 'body';

    // init the api since we'll be using calls to it
    $b.api.init(APP_URL);

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


    $b.mobilestate = {
        'url': '',
        'page': 0,
        'count': 10,
        'func': "",             // used for what type of thing are we looking at, load_recent
        'terms': [],
        'query_params': "",
        'clear': function () {
            $b.mobilestate.url = "";
            $b.mobilestate.page = 0;
            $b.mobilestate.count = 10;
            $b.mobilestate.terms = [];
            $b.mobilestate.query_params = "";
        }
    };


    /**
     * Once the page is loaded, perform some nice basics we need
     *
     */
    $b.load = function (ev) {};


    $b.load_recent = function (ev, extra_params) {
        // don't do what the click says yet
        ev.preventDefault();
        $.mobile.pageLoading();

        $b.mobilestate.func = $b.events.RECENT;
        data_home = extra_params.data_home;

        $b.api.recent($b.api.pager($b.mobilestate.page, $b.mobilestate.count),
                      {
                          // on success update the page count and update the
                          // results list
                          'success': function (data) {
                              if (data.success === true) {
                                  var page = data.payload.page;
                                  $b.mobilestate.page = page;
                                  $b.ui.results.update(data.payload.bmarks,
                                                       'Recent: Page ' + page,
                                                       data_home);
                              } else {
                                  console.error('ERROR getting recent');
                              }

                              $.mobile.pageLoading(true);
                          },
                          // once success is done updating results page, switch over
                          // there
                          'complete': function () {
                              if (data_home !== '#home_recent') {
                                  $.mobile.changePage('#results',
                                                      'slide',
                                                      back=false,
                                                      changeHash=false);
                              }

                              $.mobile.pageLoading(true);
                          }
                      }
                );
    };


    $b.load_popular = function (ev, extra_params) {
        // don't do what the click says yet
        ev.preventDefault();
        $.mobile.pageLoading();

        $b.mobilestate.func = $b.events.POPULAR;
        data_home = extra_params.data_home;

        var pager = $b.api.pager($b.mobilestate.page,
                                 $b.mobilestate.count);

        $b.api.popular(pager,
            {
                'success': function (data) {
                    if (data.success === true) {
                        var page = data.payload.page;
                        $b.mobilestate.page = page;
                        $b.ui.results.update(data.payload.bmarks,
                                             'Popular: Page ' + page,
                                             data_home);
                    } else {
                        console.error('ERROR getting popular');
                    }

                    $.mobile.pageLoading(true);
                },
                'complete': function () {
                    $.mobile.changePage('#results',
                                        'slide',
                                        back=false,
                                        changeHash=false);
                    $.mobile.pageLoading(true);
                }
            }
        );
    };


    /**
     * Handle the event to load a bookmark
     * extra_params:
     *     - hash_id
     *
     */
    $b.load_bookmark = function (ev, extra_params) {
        // don't do what the click says yet
        ev.preventDefault();
        $.mobile.pageLoading();

        $b.mobilestate.func = $b.events.VIEW;

        $b.api.bookmark(extra_params.hash_id,
                {
                    'success': function (data) {
                        if (data.success === true) {
                            var bmark = data.payload.bmark;
                            $view = $('#view_content');

                            $view.html("");

                            // let's pretty up a date for diplay
                            pretty_date = new Date(bmark.stored);
                            bmark.pretty_date = pretty_date;

                            $("#view_template").tmpl([bmark]).prependTo($view);

                        } else {
                            console.error('ERROR getting bookmark');
                        }

                    },
                    'complete': function () {
                        $.mobile.changePage('#view', 'slide', back=false, changeHash=true);
                        $.mobile.pageLoading(true);
                    }
                }
        );
    };


    $b.search = function (ev, extra_params) {
        // search for a url given the search content
        var terms, with_content, data_home;

        // don't do what the click says yet
        ev.preventDefault();

        $.mobile.pageLoading();

        terms = extra_params.terms;
        with_content = extra_params.with_content;

        // if the terms are undefined, check if we have any from a previous
        // page call
        if (terms === undefined) {
            terms = $b.mobilestate.terms;
        } else {
            $b.mobilestate.terms = terms;
        }

        if (with_content === undefined) {
            with_content = $b.mobilestate.query_params;
        } else if (with_content === "true") {
            $b.mobilestate.query_params = "&content=" + extra_params.with_content;
        }

        // the id of the <ul> we're sticking results into
        // (home page vs results page)
        data_home = extra_params.data_home;

        $b.mobilestate.func = $b.events.SEARCH;
        $b.api.search($b.mobilestate.terms,
                      with_content,
                      $b.api.pager($b.mobilestate.page, $b.mobilestate.count),
                      {
                          'success': function (data) {
                              if (data.success === true) {
                                  var page = data.payload.page,
                                      page_title = "Search: " + data.payload.phrase;


                                  if ($b.mobilestate.query_params !== "") {
                                      page_title = page_title + "<br /> (searching cached content)";
                                  }

                                  $b.mobilestate.page = page;

                                  $b.ui.results.update(data.payload.search_results,
                                                       page_title,
                                                       data_home);
                              } else {
                                  console.error('ERROR getting search');
                              }
                          },
                          'complete': function () {
                              $.mobile.changePage('#results', 'slide', back=false, changeHash=false);
                              $.mobile.pageLoading(true);
                          }
                      }
        );

    };


    /**
     * We want to manage all aspects of the results page content
     *
     */
    $b.ui.results = {
        'tpl_id': '#resultLink',
        'title_id': '#results_title',
        'update': function (data, title, data_home) {
            var page = $b.mobilestate.page;
            $(data_home).html("");

            $("#resultLink").tmpl(data).prependTo(data_home);
            $($b.ui.results.title_id).html(title);

            // this isn't always init'd so need to init it first
            $(data_home).listview('refresh');

            // now bind the swipe event to allow following of the links
            $('.bookmark_link').bind('click', function (ev) {
                ev.preventdefault();
                // the url we need to call is /redirect/hash_id
                var hash_id = $(this).attr('data-hash'),
                    url = APP_URL + "/redirect/" + hash_id,
                    newwindow = window.open(url, '_blank');

                newwindow.focus();
                return false;
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
        var button_list = {
            'go_recent': $b.events.RECENT,
            'go_popular': $b.events.POPULAR,
            'go_search': $b.events.SEARCH,
        },

        nav_buttons = function (id, event_id, data_home, callback) {
            if (callback !== undefined) {
                $($b.EVENTID).bind(event_id, callback);
            }

            $('.' + id).bind('click', function (ev) {
                $b.mobilestate.clear();
                console.log(callback);

                if (callback !== undefined) {
                    ev.preventDefault();
                    $($b.EVENTID).trigger(event_id, {data_home: data_home});
                }

                for (button in button_list) {
                    if (button == id) {
                        // then we addClass this one
                        $('.' + id).addClass('ui-btn-active ui-state-persist');
                    } else {
                        // then we remove the classes
                        $('.' + id).removeClass('ui-btn-active ui-state-persist');
                    }
                }
            });
        };

        nav_buttons('go_recent', $b.events.RECENT, '#results_list', $b.load_recent);
        nav_buttons('go_popular', $b.events.POPULAR, '#results_list', $b.load_popular);
        nav_buttons('go_search');

        $('#results_previous').bind('click', function (ev) {
            $b.mobilestate.page = $b.mobilestate.page - 1;
            $($b.EVENTID).trigger($b.mobilestate.func, {data_home: '#results_list'});
        });

        $('#results_next').bind('click', function (ev) {
            $b.mobilestate.page = $b.mobilestate.page + 1;
            $($b.EVENTID).trigger($b.mobilestate.func, {data_home: '#results_list'});
        });

        $($b.EVENTID).bind($b.events.SEARCH, $b.search);
        $('.search_form').bind('submit', function (ev) {
            var my_form_id, input_id, terms, with_content;
            console.log('triggered search');

            ev.preventDefault();

            // clear any previous search info
            $b.mobilestate.clear();

            // the terms need to be pulled from the search box
            my_form_id = $(this).attr('id');
            input_id = "#" + my_form_id + " input";

            // if this is the main search form, then check with_content
            with_content = false;

            if (my_form_id === 'search_page') {
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
            $b.mobilestate.count = 5;
            $('.listview').listview();
            $($b.EVENTID).trigger($b.events.RECENT, {data_home: '#home_recent'});
        });

        $($b.EVENTID).bind($b.events.VIEW, $b.load_bookmark);
    };

    return $b;

})(bookie || {}, jQuery);
