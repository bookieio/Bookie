<%def name="account_nav()">
    <%
        route_name = request.matched_route.name
    %>
    <ul class="tabs">
        <li ${check_selected('user_account', route_name)} class="details"><a href="${request.route_url('user_account', username=request.user.username)}">Details</a></li>
        <li ${check_selected('stats', route_name)}><a href="${request.route_url('user_stats', username=request.user.username)}">Stats</a></li>
        <li class="export"><a href="${request.route_url('user_export', username=request.user.username)}">Export</a></li>
        <li ${check_selected('user_import', route_name)}><a href="${request.route_url('user_import', username=request.user.username)}">Import</a></li>
        <li class="logout"><a href="${request.route_url('logout')}">Logout</a></li>
    </ul>
</%def>

<%def name="check_selected(nav_page, route_name)">
    % if nav_page == route_name:
        class="selected ${nav_page}"
    % else:
        class="${nav_page}"
    % endif
</%def>

<%def name="password_reset(user, reset)">
    <%
        if user.activation and user.activation.created_by == u'invite':
            title = "Please activate your new Bookie account"
            submit = "Activate"
        elif reset:
            title = "Reactivate account by resetting your password"
            submit = "Reset"
        else:
            title = "Change password"
            submit = "Change"
    %>
    <div class="form">
        <a href="#" id="show_password" class="heading">
            <span aria-hidden="true" class="icon icon-lock" title="Change
            password"></span>
            <em class="icon">change password</em>
            ${title}
        </a>

        <div id="password_change"
            % if not reset:
                style="display: none; opacity: 0;"
            % endif
        >
            <form id="password_reset" method="POST">
                % if message:
                    <div class="error">${message}</div>
                % endif
                 % if reset:
                     <input type="hidden" name="username" id="username" value="${user.username}" />
                     <input type="hidden" name="code" id="code" value="${user.activation.code}" />
                 % endif

                <div></div
                <ul>
                    % if not reset:
                        <li>
                            <label>Current Password</label>
                            <input type="password" id="current_password" name="current_password" />
                        </li>
                    % endif

                    % if user.activation and user.activation.created_by == u'invite':
                        <li>
                            <label>Choose Username</label>
                            <input type="text" id="new_username" name="new_username" />
                        </li>
                    % endif

                    <li>
                        <label>New Password</label>
                        <input type="password" id="new_password" name="new_password" />
                    </li>

                    <li>
                        <label></label>
                        <input type="submit" id="submit_password_change" value="${submit}" class="button" />
                    </li>
                </ul>
            </form>
        </div>
        <div id="password_msg" class="error" style="opacity: 0;"></div>
    </div>
</%def>
