<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <meta name="viewport" content="width=device-width, minimum-scale=1, maximum-scale=1">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />

        <link href="http://code.jquery.com/mobile/latest/jquery.mobile.min.css" rel="stylesheet" type="text/css" />
        <link rel="apple-touch-icon" href="/static/images/logo.128.png" />

        <script src="http://code.jquery.com/jquery-1.5.2.min.js"></script>


        % if hasattr(self, 'header'):
            ${self.header()}
        % endif
        <script type="text/javascript" charset="utf-8">
            <%
                app_url = request.route_url('home').rstrip('/')
            %>
            APP_URL = '${app_url}';
        </script>
    </head>

    <body class="ui-mobile-viewport">
        ${next.body()}
    </body>

    <script type="text/javascript" src="/static/js/mobile.js"></script>
    <script type="text/javascript">

        $(document).bind("mobileinit", function() {
            // do not do form submissions via ajax by default. We catch and
            // override them to handle things manually
            $.mobile.ajaxFormsEnabled = false;
            bookie.init();
        });

        $(document).ready(function () {
            $(bookie.EVENTID).trigger(bookie.events.LOAD);
        });

    </script>
    <!--<script src="http://code.jquery.com/mobile/latest/jquery.mobile.min.js"></script>-->
    <script src="http://code.jquery.com/mobile/1.0a4.1/jquery.mobile-1.0a4.1.min.js"></script>

    <script src="http://ajax.aspnetcdn.com/ajax/jquery.templates/beta1/jquery.tmpl.min.js"></script>
</html>
