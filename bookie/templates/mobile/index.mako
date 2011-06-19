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

        h1 span {
            font-size: smaller;
            color: #363d52;
            opacity: 70%;
        }

        .center {
            text-align: center;
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

        .ui-navbar {
            max-height: 50px;
        }

        .footer.ui-navbar {
            max-height: 37px;
        }

    </style>


</%def>

<div data-role="page" id="home">

    <header data-role="header" class="head">
        <h1>Bookie  <span>- bookmark your web</span</h1>
    </header>

    <div data-role="content">

        <form action="#" method="get" class="search_form" id="footer_search">
            <input type="search" name="home_search" id="home_search"
                   class="search" placeholder="search..."/>
        </form>

        <h3>Recent Additions</h3>
        <ul data-role="listview" data-split-icon="gear" data-split-theme="c" data-theme="c" id="home_recent" class="listview">
        </ul>
    </div>

    <footer data-id="nav" data-role="footer" data-type="horizontal"
            data-position="fixed" class="footer" role="contentinfo">
        <div data-role="navbar" role="navigation">
            <ul>
                <li>
                    <a href="#results" class="go_recent" data-role="button"
                                data-inline="true" data-theme="a"
                                data-icon="grid"
                                data-iconpos="right">Recent</a>
                </li>
                <li>
                    <a href="#results" class="go_popular" data-role="button"
                                data-inline="true" data-theme="a"
                                data-icon="star"
                                data-iconpos="right">Popular</a>
                </li>
                <li>
                    <a href="#search" class="go_search" data-role="button"
                       data-inline="true" data-theme="a"
                       data-icon="search"
                       data-iconpos="top">Search</a>
                </li>
             </ul>
         </div>
    </footer>

</div>

<div data-role="page" id="search">
    <header data-role="header" class="head">
        <h1>Search</h1>
    </header>

    <div data-role="content">
        <form action="#" method="GET" class="search_form" id="search_page">
            <div data-role="fieldcontain">
                <label for="cache_content">Include Content?</label>
                <select name="cache_content" id="cache_content" data-role="slider" data-inline="true">
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                </select>
            </div>
            <div data-role="fieldcontain">
                <input type="search" id="search" placeholder="enter keywords..." />
            </div>
        </form>
    </div>
    <footer data-id="nav" data-role="footer" data-type="horizontal"
            data-position="fixed" class="footer" role="contentinfo">
        <div data-role="navbar" role="navigation">
            <ul>
                <li>
                    <a href="#results" class="go_recent" data-role="button"
                                data-inline="true" data-theme="a"
                                data-icon="grid"
                                data-iconpos="right">Recent</a>
                </li>
                <li>
                    <a href="#results" class="go_popular" data-role="button"
                                data-inline="true" data-theme="a"
                                data-icon="star"
                                data-iconpos="right">Popular</a>
                </li>
                <li>
                    <a href="#search" class="go_search" data-role="button"
                       data-inline="true" data-theme="a"
                       data-icon="search"
                       data-iconpos="top">Search</a>
                </li>
             </ul>
         </div>
    </footer>



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
        <ul data-role="listview" data-split-icon="gear" data-split-theme="c"
            data-theme="c" id="results_list" class="listview">
            <li>No results</li>
        </ul>
    </div>

    <footer data-id="nav" data-role="footer" data-type="horizontal"
            data-position="fixed" class="footer" role="contentinfo">
        <div data-role="navbar" role="navigation">
            <ul>
                <li>
                    <a href="#results" class="go_recent" data-role="button"
                                data-inline="true" data-theme="a"
                                data-icon="grid"
                                data-iconpos="right">Recent</a>
                </li>
                <li>
                    <a href="#results" class="go_popular" data-role="button"
                                data-inline="true" data-theme="a"
                                data-icon="star"
                                data-iconpos="right">Popular</a>
                </li>
                <li>
                    <a href="#search" class="go_search" data-role="button"
                       data-inline="true" data-theme="a"
                       data-icon="search"
                       data-iconpos="top">Search</a>
                </li>
             </ul>
        </div>
    </footer>

    <script id="resultLink" type="text/x-jquery-tmpl">
        <li>
            <a href="#"
               data-hash="${'${hash_id}'|n}"
               rel="external" target="_blank" class="bookmark_link">
                    <h3>${'${description}'|n}</h3>
                    <p>
                        {{each tags}}
                            ${'${$value.name}'}&nbsp;&nbsp;
                        {{/each}}
                    </p>
            </a>
            <a href="#"
               data-hash="${'${hash_id}'|n}"
               class="bookmark_view"></a>
        </li>
    </script>

</div>

<div data-role="page" id="view">

    <header data-role="header" class="head">
        <h1 id="view_title">Details</h1>
    </header>

    <div data-role="content" id="view_content">

    </div>

    <script id="view_template" type="text/x-jquery-tmpl">
        <h3 id="view_desc">
            <a href="${request.route_url('home').rstrip('/')}/${username}/redirect/${'${hash_id}'|n}"
                rel="external" target="_blank">
                ${'${description}'|n}
            </a>
        </h3>
        <p id="view_tags"><strong>${'${tag_str}'|n}</strong></p>
        <p id="view_date">
            ${'${pretty_date.toDateString()}'|n}
        </p>
        <p id="view_extended">${'${extended}'|n}</p>
        {{if readable}}
            <p id="view_content">${'{{html readable.content}}'|n}</p>
        {{/if}}
    </script>
</div>
