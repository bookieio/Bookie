<%inherit file="/main_wrap.mako" />
<%def name="title()">Account Information: ${user.username}</%def>

<h1>Account Information</h1>

<ul class="tabs">
    <li class="selected"><a href="${request.route_url('user_account', username=request.user.username)}">Details</a></li>
    <li><a href="">Stats</a></li>
    <li><a href="${request.route_url('user_export', username=request.user.username)}">Export</a></li>
    <li><a href="${request.route_url('user_import', username=request.user.username)}">Import</a></li>
    <li><a href="${request.route_url('logout')}">Logout</a></li>
</ul>

<ul>
    <li>${user.username}</li>
    <li>${user.name}</li>
    <li>${user.email}</li>
    <li>${user.signup}</li>
    <li>${user.last_login}</li>
</ul>
