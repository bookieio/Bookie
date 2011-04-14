<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <link rel="stylesheet" type="text/css"
        href="http://yui.yahooapis.com/combo?3.3.0/build/cssreset/reset-min.css&3.3.0/build/cssfonts/fonts-min.css&3.3.0/build/cssgrids/grids-min.css&3.3.0/build/cssbase/base-min.css">

        <link rel="stylesheet" type="text/css" href="/static/css/bookie.css">

        % if hasattr(self, 'header'):
            ${self.header()}
        % endif
    </head>

    <body>
        <div id="navigation" class="yui3-g">
            <div class="yui3-u-2-3"><a href="/recent" class="logo">Logo/Title</a></div>
            <div class="yui3-u-1-3 navigation">
                <span class="item"><a href="/recent" class="button_minimal">Recent</a></span>
                <span class="item"><a href="/popular" class="button_minimal">Popular</a></span>
                <span class="item"><a href="/tags" class="button_minimal">Tags</a></span>
                <span class="item">
                    <span class="button_minimal">
                         <form action="${request.route_url('search')}" method="get"/>
                             <input type="search" name="search" id="search" placeholder="search.." />
                             <input type="checkbox" name="content" id="search_content"  /> Content
                         </form>
                    </span>
                </span>
            </div>
        </div>
        <div id="body">
            ${next.body()}
        </div>

        <div class="footer">
            <div class="yui3-g">
            <div class="yui3-u-1-4"></div>
            <div class="yui3-u-3-4">
                <div class="right">
                    <a href="http://bmark.us">Bookie</a> |
                    <a href="http://https://github.com/mitechie/Bookie/issues">Support</a> |
                    <a href="#changelog">Changes</a> |
                    <a href="${request.route_url('import')}">Import</a> |
                    <a href="${request.route_url('export')}">Export</a>
                </div>
            </div>
            </div>
        </div>
    </body>
</html>
