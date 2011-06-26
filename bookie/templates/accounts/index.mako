<%inherit file="/main_wrap.mako" />
<%def name="title()">Account Information: ${user.username}</%def>

<h1>Account Information</h1>

<ul>
    <li>${user.username}</li>
    <li>${user.email}</li>
    <li>${user.last_login}</li>
</ul>


Need controls here for 
<ul>
    <li>Logout</li>
    <li>import</li>
    <li>export</li>
    <li>api_key</li>
</ul>
