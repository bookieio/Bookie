<%inherit file="/wrapper.mako" />
<%def name="title()">User Login</%def>
<html>
<head>
<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>

</head>

<body style="text-align: center;">
    <div style="margin: auto; text-align: center; width: 475;">
        <p>&nbsp;</p>
        <h2>Welcome to the Quipp</h2>
        <p>&nbsp;</p>
        <fieldset style="margin: auto; float: none;">
            <div class="fieldset_legend">Log into Quipp Site</div>

            %if c.login_counter > 0 or c.login_failed:
                <div class="error">Incorrect username or password.
                    <br />Please contact R&D for support if you believe this is an
                    error.
                </div>
            %endif

            <form id="login_form" action="${h.url('/login_handler', came_from=c.came_from, __logins=c.login_counter)}" method="POST">
                <ol class="form">
                    <li formfield="login">
                        <label for="login" style="float: none;">Username:</label>
                        ${h.text('login', id="login", class_="form", placeholder="Enter your username...")}
                    </li>
                    <li formfield="login">
                        <label for="login" style="float: none;">Password:</label>
                        ${h.password('password', id="password", class_="form", placeholder="Enter your password...")}
                    </li>

                    <li formfield="submit">
                        <input type="submit" id="submit" value="Login" class="form" />
                    </li>

                </ol>
            </form>
        </fieldset>
    </div>
    <%def name="add_js()">

        <script type="text/javascript">
            qp.login();
        </script>

    </%def>
</body>
</html>
