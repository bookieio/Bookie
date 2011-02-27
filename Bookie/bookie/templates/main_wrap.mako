<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/combo?3.3.0/build/cssreset/reset-min.css&3.3.0/build/cssfonts/fonts-min.css&3.3.0/build/cssgrids/grids-min.css">

        % if hasattr(self, 'header'):
            ${self.header()}
        % endif

        <style type="text/css">
            .data_list {
                width: 80%;
            }

            .data_list .bmark {
                padding: .2em;
            }

            #body {
                margin: 1em;
            }
        </style>

    </head>

    <body>
        <div id="body">
            ${next.body()}
        </div>
    </body>
</html>
