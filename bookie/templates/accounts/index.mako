<%inherit file="/main_wrap.mako" />
<%def name="title()">Account Information: ${user.username}</%def>
<%namespace file="func.mako" import="account_nav"/>
<%
    date_fmt = "%m/%d/%Y"
%>
${account_nav()}

<div class="form">
    <form>
        <ul>
            <li>
                <label>Username</label>
                <span>${user.username}</span>
            </li>
            <li>
                <label>Name</label>
                <input type="text" id="name" name="name" value="${user.name}" />
            </li>
            <li>
                <label>Email</label>
                <input type="text" id="email" name="email" value="${user.email}" />
            </li>
            <li>
                <label>Signup Date</label>
                <span>
                    % if user.signup:
                        ${user.signup.strftime(date_fmt)}
                    % else:
                        Unknown
                    % endif
                </span>
            </li>
            <li>
                <label>Last Login</label>
                <span>${user.last_login.strftime(date_fmt)}</span>
            </li>
        </ul>
    </form>
</div>

<div class="form">
    <a href="" id="show_key" class="heading">View API Key</a>
    <div id="api_key_container" style="display: none;">
        <form>
            <ul>
                <li>
                    <label>Api Key</label>
                    <span id="api_key"></span>
                </li>
            </ul>
            <div class="details">
            Your Api Key is used to validate your account when using outside
            services. This includes anything making Api calls on your behalf such
            as the mobile site, outside scripts, or client applications.
            </div>
        </form>
    </div>
</div>

<div class="form">
    <a href="#" id="show_password" class="heading">Reset Password</a>
    <div id="password_change" style="display: none;">
        <form>
            <ul>
                <li>
                    <label>Current Password</label>
                    <input type="password" id="current_password" name="current_password" />
                </li>

                <li>
                    <label>New Password</label>
                    <input type="password" id="new_password" name="new_password" />
                </li>

                <li>
                    <label></label>
                    <input type="button" id="submit_password_change" value="Change" class="button" />
                </li>
            </ul>
        </form>
    </div>
    <div id="password_msg" class="error"></div>
</div>

<%def name="add_js()">
    <script type="text/javascript">
        $(document).ready(function() {
            bookie.accounts.init();
        });
    </script>
</%def>
