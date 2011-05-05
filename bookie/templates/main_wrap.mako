<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <link type="text/css" href="/static/css/ui-lightness/jquery-ui-1.8.11.custom.css" rel="Stylesheet" />
        <link rel="stylesheet" type="text/css"
        href="http://yui.yahooapis.com/combo?3.3.0/build/cssreset/reset-min.css&3.3.0/build/cssfonts/fonts-min.css&3.3.0/build/cssgrids/grids-min.css&3.3.0/build/cssbase/base-min.css">

        <link href='http://fonts.googleapis.com/css?family=Cabin' rel='stylesheet' type='text/css'>
        <link href='http://fonts.googleapis.com/css?family=Cabin+Sketch:bold' rel='stylesheet' type='text/css'>

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
                <!--<span class="item"><a href="/popular" class="nav_button">Popular</a></span>-->
                <span class="item"><a href="/search" class="nav_button">Search</a></span>
                <!--<span class="item">-->

                <!--</span>-->
            </div>
        </div>
        <div id="body">
            <div class="yui3-g">
                <div class="yui3-u-1">
                    ${next.body()}
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

        <script type="text/javascript" src="/static/js/lib/jquery.min.js"></script>
        <script type="text/javascript" src="/static/js/lib/jquery-ui-1.8.11.custom.min.js"></script>
        <script type="text/javascript" src="/static/js/bookie.js"></script>

        <script type="text/javascript">
            $(document).ready(function() {
                bookie.init();
            });
        </script>
    </body>
</html>
