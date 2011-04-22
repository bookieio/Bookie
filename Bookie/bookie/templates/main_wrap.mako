<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <link rel="stylesheet" type="text/css"
        href="http://yui.yahooapis.com/combo?3.3.0/build/cssreset/reset-min.css&3.3.0/build/cssfonts/fonts-min.css&3.3.0/build/cssgrids/grids-min.css&3.3.0/build/cssbase/base-min.css">

        <link href='http://fonts.googleapis.com/css?family=Cabin' rel='stylesheet' type='text/css'>
        <link rel="stylesheet" type="text/css" href="/static/css/bookie.css">

        % if hasattr(self, 'header'):
            ${self.header()}
        % endif
    </head>

    <body>
        <div id="navigation" class="yui3-g">
            <div class="yui3-u-2-3">
                <div class="logo">
                    <a href="/recent" class="logo">Bookie</a>
                    <span class="alt_logo">&nbsp;&#45; bookmark your web</span>
                </div>
            </div>
            <div class="yui3-u-1-3 navigation">
                <span class="item"><a href="/recent" class="nav_button">Recent</a></span>
                <span class="item"><a href="/popular" class="nav_button">Popular</a></span>
                <!--<span class="item"><a href="/tags" class="button_minimal">Tags</a></span>-->
                <!--<span class="item">-->

                <!--</span>-->
            </div>
        </div>
        <div id="body">
            <div class="yui3-g">
                <div class="yui3-u-4-5">
                    ${next.body()}
                </div>

                <div class="yui3-u-1-5">
                    <div class="search">
                        <h2 class="title">Search</h2>
                        <div class="body">
                            <form action="${request.route_url('search')}" method="get"/>
                                <input type="search" name="search" id="search"
                                    placeholder="keywords.." />
                                <br />
                                <input type="checkbox" name="content"
                                id="search_content"  /> In Cached Content
                                <br />
                                <input style="line-height: 1.5;" type="submit" name="submit" class="button" id="submit_search" value="Search"/>
                            </form>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <div class="footer">
            <div class="yui3-g">
            <div class="yui3-u-1-4"></div>
            <div class="yui3-u-3-4">
                <div class="right body">
                    <a href="http://bmark.us">Bookie</a> |
                    <a href="http://github.com/mitechie/Bookie/issues">Support</a> |
                    <a href="#changelog">Changes</a> |
                    <a href="${request.route_url('import')}">Import</a> |
                    <a href="${request.route_url('export')}">Export</a>
                </div>
            </div>
            </div>
        </div>
    </body>
</html>
