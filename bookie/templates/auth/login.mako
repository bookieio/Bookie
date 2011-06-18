<%inherit file="/main_wrap.mako" />
<%def name="title()">Login</%def>

<h1>Log In</h1>

<p>${message}</p>

<div class="login_form">
    <form action="${request.route_url('login')}" method="post" class="login">
        <input type="hidden" name="came_from" value="${came_from}"/>
        <input type="text" name="login" value="${login}"/>
        <br/>
        <input type="password" name="password" value="${password}"/>
        <br/>
        <input type="submit" name="form.submitted" value="Log In"/>
    </form>
</div>
