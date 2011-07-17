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
     * Handle our paging keep tabs on counts, page number, etc
     *
     */
    $b.pagination = {
        'page': 0,
        'count': 10,
        'terms': [],
        'query_params': "",
        'clear': function () {
            $b.pagination.page = 0;
            $b.pagination.count = 10;
            $b.pagination.terms = [];
            $b.pagination.query_params = "";
        }
    };


    /**
     * Handling our history stack and changing pages back/forth overriding
     * jquerymobile
     *
     */
    var PageControl = function() {
        var process, that = {};
        that.current_page = undefined;

        /**
         * Perform the history alteration
         *
         */
        process = function (page, nochange) {
            that.current_page = page;

            // now run the function
            page.load(page.data);
        };

        /**
         * forward will not only perform the load function, but also change the
         * page
         *
         */
        that.forward = function(page) {
            alert("FORWARD");
            history.pushState(page, null, page.id);

            $.mobile.pageLoading();
            $.mobile.changePage(page.id, 'slide', back=false, changeHash=false);
            process(page);
            // and remove the loading icon
            $.mobile.pageLoading(true);
        };

        /**
         * manual will only perform the load function. This is handy if we're
         * already on the page or for loading the home page content
         *
         */
        that.manual = function (page) {
            alert("MANUAL");
            process(page, true);
        };

        /**
         * Pop the history stack and run the load function for the page
         * requested
         *
         */
        that.backward = function(page) {
            if (page !== null) {
                alert('BACKWARD');
                // this page is from the history api which somehow removes my
                // functions so we need to get the function to call
                var func_name = page.id.substr(1);
                page.load = $b.pages[func_name].load;

                $.mobile.pageLoading();
                $.mobile.changePage(page.id, 'slide', back=false, changeHash=false);
                page.load(page.data);
                $.mobile.pageLoading(true);
            } else {
                alert('back too far, should hopefully be at home page');
                // the default page to load is the home page?
                page = $b.pages.home;
                that.manual(page);
            }
        };

        return that;
    };


    /**
     * List of pages of content we support.
     *
     * Each page has
     *  - a page id
     *  - data needed for loading that page
     *  - the load * function itself that the history code will call
     *
     */
    $b.pages = {
        'home': {
            'id': '#home',
            'data': {'data_home': '#home_recent'},
            'call': 'load',
            'load': function (page_data) {
                // we only want to load 5 for the home page
                $b.pagination.count = 5;
                $b.pagination.page = 0;

                $b.api.recent($b.api.pager($b.pagination.page, $b.pagination.count), {
                    // on success update the page count and update the
                    // results list
                    'success': function (data) {
                        if (data.success === true) {
                            var page = data.payload.page;
                            $b.pagination.page = 0;
                            $b.ui.results.update(data.payload.bmarks,
                                                 'Bookie Bookmarks',
                                                 page_data.data_home);
                        } else {
                            console.error('ERROR getting recent');
                        }
                    },
                });
            }
        },

        'recent': {
            'id': '#results',
            'data': {'data_home': '#results_list'},
            'call': 'load',
            'load': function (page_data) {
                $b.api.recent($b.api.pager($b.pagination.page, $b.pagination.count), {
                    // on success update the page count and update the
                    // results list
                    'success': function (data) {
                        if (data.success === true) {
                            var page = data.payload.page;
                            $b.pagination.page = page;
                            $b.ui.results.update(data.payload.bmarks,
                                                 'Recent: Page ' + page,
                                                 page_data.data_home);
                        } else {
                            console.error('ERROR getting recent');
                        }
                    },
                });
            }
        },

        'popular': {
            'id': '#results',
            'data': {'data_home': '#results_list'},
            'call': 'load',
            'load': function (page_data) {
                var pager = $b.api.pager($b.pagination.page,
                                         $b.pagination.count);

                $b.api.popular(pager, {
                        'success': function (data) {
                            if (data.success === true) {
                                var page = data.payload.page;
                                $b.pagination.page = page;
                                $b.ui.results.update(data.payload.bmarks,
                                                     'Popular: Page ' + page,
                                                     page_data.data_home);
                            } else {
                                console.error('ERROR getting popular');
                            }

                            $.mobile.pageLoading(true);
                        },
                    }
                );
            }
        },

        'view': {
            'id': '#view',
            'data': {},
            'call': 'load',
            'load': function (page_data) {
                $b.api.bookmark(page_data.hash_id, {
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

                    }
                });
            }
        },

        'search': {
            'id': '#search',
            'data': {},
            'call': 'load',
            'load': function (page_data) {
                $('.search_form').bind('submit', function (ev) {
                    var my_form_id, input_id, terms, with_content;
                    console.log('triggered search');
                    ev.preventDefault();

                    // the terms need to be pulled from the search box
                    my_form_id = $(this).attr('id');
                    input_id = "#" + my_form_id + " input";

                    // if this is the main search form, then check with_content
                    with_content = false;

                    if (my_form_id === 'search_page') {
                        with_content = $("#cache_content").val();
                    }

                    terms = $(input_id).val().split(" ");

                    $b.pages.results.data = {terms: terms,
                                                    with_content: with_content,
                                                    data_home: '#results_list'}
                    $b.pc.forward($b.pages.results);
                });
            }
        },

        'results': {
            'id': '#results',
            'data': {'data_home': '#results_list'},
            'call': 'load',
            'load': function (page_data) {
                var terms = page_data.terms,
                    with_content = page_data.with_content,
                    data_home = page_data.data_home;

                // if the terms are undefined, check if we have any from a previous
                // page call
                if (terms === undefined) {
                    terms = $b.pagination.terms;
                } else {
                    $b.pagination.terms = terms;
                }

                if (with_content === undefined) {
                    with_content = $b.pagination.query_params;
                } else if (with_content === "true") {
                    $b.pagination.query_params = "&content=" + with_content;
                }

                // the id of the <ul> we're sticking results into
                // (home page vs results page)
                data_home = page_data.data_home;

                $b.api.search(
                    $b.pagination.terms,
                    with_content,
                    $b.api.pager($b.pagination.page, $b.pagination.count),
                    {
                        'success': function (data) {
                            if (data.success === true) {
                                var page = data.payload.page,
                                    page_title = "Search: " + data.payload.phrase;

                                if ($b.pagination.query_params !== "") {
                                    page_title = page_title + "<br /> (searching cached content)";
                                }

                                $b.pagination.page = page;
                                $.mobile.changePage('#results',
                                                    'slide',
                                                    back=false,
                                                    changeHash=false);
                                $b.ui.results.update(data.payload.search_results,
                                                     page_title,
                                                     data_home);
                            } else {
                                console.error('ERROR getting search');
                            }
                        }
                    });
            }
        }

    };


    /**
     * We want to manage all aspects of the results page content
     *
     */
    $b.ui.results = {
        'tpl_id': '#resultLink',
        'title_id': '#results_title',
        'update': function (data, title, data_home) {
            var page = $b.pagination.page;
            $(data_home).html("");
            $(data_home).listview('destroy');

            $("#resultLink").tmpl(data).appendTo(data_home);
            $($b.ui.results.title_id).html(title);

            // this isn't always init'd so need to init it first
            $(data_home).listview();

            // now bind the event to allow following of the links
            $('.bookmark_link').bind('click', function (ev) {
                ev.preventDefault();
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
                $b.pages.bookmark.data = {'hash_id': hash_id};
                $b.pc.forward($b.pages.view);
            });

            $(data_home).listview('refresh');
        }
    };


    // only need to call init on the page read event
    $b.init = function () {
        $b.pc = PageControl();

        window.addEventListener("popstate", function(ev) {
            ev.preventDefault();
            console.log(ev);
            $b.pc.backward(ev.state);
        });

        window.addEventListener('unload', function(ev) {
            console.log('unload');
            ev.preventDefault();
        });

        // bind the recent button
        $('.go_recent').bind('click', function (ev) {
            ev.preventDefault();
            $b.pagination.clear();
            $b.pc.forward($b.pages.recent);
        });

        $('.go_popular').bind('click', function (ev) {
            ev.preventDefault();
            $b.pagination.clear();
            $b.pc.forward($b.pages.popular);
        });

        $('.go_search').bind('click', function (ev) {
            ev.preventDefault();
            $b.pagination.clear();
            $b.pc.forward($b.pages.search);
        });

    };

    // $b.search = function (ev, extra_params) {
    //     // search for a url given the search content
    //     var terms, with_content, data_home;

    //     // don't do what the click says yet
    //     ev.preventDefault();

    //     $.mobile.pageLoading();

    //     terms = extra_params.terms;
    //     with_content = extra_params.with_content;

    //     // if the terms are undefined, check if we have any from a previous
    //     // page call
    //     if (terms === undefined) {
    //         terms = $b.pagination.terms;
    //     } else {
    //         $b.pagination.terms = terms;
    //     }

    //     if (with_content === undefined) {
    //         with_content = $b.pagination.query_params;
    //     } else if (with_content === "true") {
    //         $b.pagination.query_params = "&content=" + extra_params.with_content;
    //     }

    //     // the id of the <ul> we're sticking results into
    //     // (home page vs results page)
    //     data_home = extra_params.data_home;

    //     $b.pagination.func = $b.events.SEARCH;
    //     $b.api.search($b.paginatino.terms,
    //                   with_content,
    //                   $b.api.pager($b.pagination.page, $b.pagination.count),
    //                   {
    //                       'success': function (data) {
    //                           if (data.success === true) {
    //                               var page = data.payload.page,
    //                                   page_title = "Search: " + data.payload.phrase;


    //                               if ($b.pagination.query_params !== "") {
    //                                   page_title = page_title + "<br /> (searching cached content)";
    //                               }

    //                               $b.pagination.page = page;
    //                               $.mobile.changePage('#results',
    //                                                   'slide',
    //                                                   back=false,
    //                                                   changeHash=false);
    //                               $b.ui.results.update(data.payload.search_results,
    //                                                    page_title,
    //                                                    data_home);
    //                           } else {
    //                               console.error('ERROR getting search');
    //                           }
    //                       },
    //                       'complete': function () {
    //                           console.log('fired complete');

    //                           $.mobile.pageLoading(true);
    //                       }
    //                   }
    //     );

    // };

        // nav_buttons = function (id, event_id, data_home, callback) {
        //     if (callback !== undefined) {
        //         $($b.EVENTID).bind(event_id, callback);
        //     }

        //     $('.' + id).bind('click', function (ev) {
        //         $b.pagination.clear();

        //         if (callback !== undefined) {
        //             ev.preventDefault();
        //             $($b.EVENTID).trigger(event_id, {data_home: data_home});
        //         }

        //         for (button in button_list) {
        //             if (button == id) {
        //                 // then we addClass this one
        //                 $('.' + id).addClass('ui-btn-active ui-state-persist');
        //             } else {
        //                 // then we remove the classes
        //                 $('.' + id).removeClass('ui-btn-active ui-state-persist');
        //             }
        //         }
        //     });
        // };

        // nav_buttons('go_recent', $b.events.RECENT, '#results_list', $b.load_recent);
        // nav_buttons('go_popular', $b.events.POPULAR, '#results_list', $b.load_popular);
        // nav_buttons('go_search');

        // $('#results_previous').bind('click', function (ev) {
        //     $b.pagination.page = $b.pagination.page - 1;
        //     $($b.EVENTID).trigger($b.pagination.func, {data_home: '#results_list'});
        // });

        // $('#results_next').bind('click', function (ev) {
        //     $b.pagination.page = $b.pagination.page + 1;
        //     $($b.EVENTID).trigger($b.pagination.func, {data_home: '#results_list'});
        // });


    return $b;

})(bookie || {}, jQuery);
