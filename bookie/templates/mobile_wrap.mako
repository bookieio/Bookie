<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />

        <link rel="stylesheet" href="http://code.jquery.com/mobile/1.0a4.1/jquery.mobile-1.0a4.1.min.css" />
        <link href='http://fonts.googleapis.com/css?family=Cabin+Sketch:bold&text=Bookie' rel='stylesheet' type='text/css'>
        <link rel="apple-touch-icon" href="/static/images/logo.128.png" />

        % if hasattr(self, 'header'):
            ${self.header()}
        % endif

    </head>

    <body class="ui-mobile-viewport">
        ${next.body()}
    </body>

    <script src="http://code.jquery.com/jquery-1.5.2.min.js"></script>
    <script type="text/javascript" src="/static/js/bookie.js"></script>
    <script src="http://code.jquery.com/mobile/1.0a4.1/jquery.mobile-1.0a4.1.min.js"></script>
    <script type="text/javascript">

        $(document).bind("mobileinit", function(){
            $.mobile.foo = bar;
        });

    </script>
</html>
