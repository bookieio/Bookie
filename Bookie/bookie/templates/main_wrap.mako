<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/combo?3.3.0/build/cssreset/reset-min.css&3.3.0/build/cssfonts/fonts-min.css&3.3.0/build/cssgrids/grids-min.css">

        <link rel="stylesheet" type="text/css" href="/static/css/bookie.css">

        % if hasattr(self, 'header'):
            ${self.header()}
        % endif
    </head>

    <body>
        <div id="navigation" class="yui3-g">
            <div class="yui3-u-3-4"><a href="/recent" class="logo">Logo/Title</a></div>
            <div class="yui3-u-1-4 navigation">
                <span class="item"><a href="/recent" class="button_minimal">Recent</a></span>
                <span class="item"><a href="/tags" class="button_minimal">Tags</a></span>
            </div>
        </div>
        <div id="body">
            ${next.body()}
        </div>
    </body>
</html>
