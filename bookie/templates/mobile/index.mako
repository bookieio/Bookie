<%inherit file="/mobile_wrap.mako" />
<%def name="title()">Bookie Bookmarks</%def>
<%def name="header()">

    <style type="text/css">
        .head {
            background: #CCCCCC;
            border-bottom: 2px solid #333;
            color: #363d52;
            font-family: Cabin,arial,helvetica,clean,sans-serif;
            text-shadow: 4px 4px 4px #CCCCCC;
            width: 100%;
        }

        .center {
            text-align: center;
        }

        .footer {
            border-top: 2px solid #333;
            background: #CCCCCC;
            color: #363d52;
        }

        .footer a.ui-link {
            color: #363d52;
            text-decoration: none;
        }

        .head h1.ui-title {
        }

        footer form {
            padding: .3em .2em;
            text-align: center;
        }

        form {
            text-align: center;
        }

        a.bookmark_link {
            font-family: Cabin,arial,helvetica,clean,sans-serif;
        }

    </style>


</%def>

<div data-role="page" id="home">

    <header data-role="header" class="head">
        <h1>Bookie</h1>
    </header>

    <div data-role="content">

        <h3>Search Bookmarks</h3>
        <form action="#" method="get" class="search_form" id="footer_search">
            <input type="search" name="home_search" id="home_search"
                   class="search" placeholder="search..."/>
        </form>

        <h3>Recent Bookmarks</h3>
        <ul data-role="listview" data-split-icon="gear" data-split-theme="c" data-theme="c" id="home_recent" class="listview">
        </ul>
    </div>

    <footer data-id="nav" data-role="navbar" data-type="horizontal" data-position="fixed" class="footer">
        <ul>
            <li>
                <a href="#results" class="go_recent" data-role="button"
                            data-inline="true" data-theme="a"
                            data-iconpos="right">Recent</a>
            </li>
            <li>
                <a href="#results" class="go_popular" data-role="button"
                            data-inline="true" data-theme="a"
                            data-iconpos="right">Popular</a>
            </li>
            <li>
                <a href="#search" class="go_search" data-role="button"
                   data-inline="true" data-theme="a"
                   data-iconpos="top">Search</a>
            </li>
         </ul>
    </footer>

</div>

<div data-role="page" id="search">
    <header data-role="header" class="head">
        <h1>Search</h1>
    </header>

    <div data-role="content">
        <form action="#search" method="GET" class="search_form" id="search_page">
            <div data-role="fieldcontain">
                <label for="cache_content">Include Content?</label>
                <select name="cache_content" id="cache_content" data-role="slider" data-inline="true">
                    <option value="off">No</option>
                    <option value="on">Yes</option>
                </select>
            </div>
            <div data-role="fieldcontain">
                <input type="search" id="search" placeholder="enter keywords..." />
            </div>
        </form>
    </div>
    <footer data-id="nav" data-role="navbar" data-type="horizontal" data-position="fixed" class="footer">
        <ul>
            <li>
                <a href="#results" class="go_recent" data-role="button"
                            data-inline="true" data-theme="a"
                            data-iconpos="right">Recent</a>
            </li>
            <li>
                <a href="#results" class="go_popular" data-role="button"
                            data-inline="true" data-theme="a"
                            data-iconpos="right">Popular</a>
            </li>
            <li>
                <a href="#search" class="go_search" data-role="button"
                   data-inline="true" data-theme="a"
                   data-iconpos="top">Search</a>
            </li>
         </ul>
    </footer>

    <script id="resultLink" type="text/x-jquery-tmpl">
        <li>
            <a href="#"
               data-hash="${'${hash_id}'|n}"
               rel="external" target="_blank" class="bookmark_link">
                    <h3>${'${description}'|n}</h3>
                    <p class="ui-li-aside">${'${tag_string}'|n}</p>
            </a>
            <a href="#"
               data-hash="${'${hash_id}'|n}"
               class="bookmark_link"></a>
        </li>
    </script>

</div>

<!-- Page for all results

    - Search Results
    - Recent bookmark results
    - Popular bookmark results

    Need to set the:
    - #results_title
    - results body
    - paging footer
-->
<div data-role="page" id="results">

    <header data-role="header" class="head">
        <h1 id="results_title">...</h1>
        <div data-role="navbar" data-type="horizontal" data-position="fixed">
            <ul>
                <li>
                    <a href="#" id="results_previous" data-role="button"
                                data-inline="true" data-theme="a"
                                data-page="0"
                                data-icon="arrow-l"
                                data-iconpos="left">Previous</a>
                </li>
                <li>
                    <a href="#" id="results_next" data-role="button"
                                data-inline="true" data-theme="a"
                                data-page="0"
                                data-icon="arrow-r"
                                data-iconpos="right">Next</a>
                </li>
             </ul>
        </div>
    </header>

    <div data-role="content">
        <ul data-role="listview" data-split-icon="gear" data-split-theme="c" data-theme="c" id="results_list" class="listview">
        </ul>
    </div>

    <footer data-id="nav" data-role="navbar" data-type="horizontal" data-position="fixed" class="footer">
        <ul>
            <li>
                <a href="#results" class="go_recent" data-role="button"
                            data-inline="true" data-theme="a"
                            data-iconpos="right">Recent</a>
            </li>
            <li>
                <a href="#results" class="go_popular" data-role="button"
                            data-inline="true" data-theme="a"
                            data-iconpos="right">Popular</a>
            </li>
            <li>
                <a href="#search" class="go_search" data-role="button"
                   data-inline="true" data-theme="a"
                   data-iconpos="top">Search</a>
            </li>
         </ul>
    </footer>

</div>
