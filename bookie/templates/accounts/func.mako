<%def name="account_nav()">
    <%
        route_name = request.matched_route.name
    %>
    <ul class="tabs">
        <li ${check_selected('user_account', route_name)}><a href="${request.route_url('user_account', username=request.user.username)}">Details</a></li>
        <li ${check_selected('stats', route_name)}><a href="#">Stats</a></li>
        <li><a href="${request.route_url('user_export', username=request.user.username)}">Export</a></li>
        <li ${check_selected('user_import', route_name)}><a href="${request.route_url('user_import', username=request.user.username)}">Import</a></li>
        <li><a href="${request.route_url('logout')}">Logout</a></li>
    </ul>
</%def>

<%def name="check_selected(nav_page, route_name)">
    % if nav_page == route_name:
        class="selected"
    % endif
</%def>
