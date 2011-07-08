<%inherit file="/main_wrap.mako" />
<%def name="title()">Login</%def>



<div class="login_form" class="block">
    <form action="${request.route_url('login')}" method="post" class="login form">
        <div class="heading">Log In</div>
        <p class="error">${message}</p>
        <input type="hidden" name="came_from" value="${came_from}"/>
        <ul>
            <li>
                <label>Username</label>
                <input type="text" name="login" value="${login}"/>
            </li>
            <li>
                <label>Password</label>
                    <input type="password" name="password" value="${password}"/>
            </li>
            <li>
                <label></label>
                <input type="submit" name="form.submitted" value="Log In"/>
            </li>
        </ul>
    </form>
</div>


<div class="block form">
    <a href="" id="show_forgotten" class="heading">Forgotten Password</a>
    <div id="forgotten_password" style="display: none;">
        <%include file="forgot.mako"/>
    </div>
</div>

<%def name="add_js()">
    <script type="text/javascript">
        $(document).ready(function() {
            bookie.login.init();
        });
    </script>
</%def>
