<%inherit file="/main_wrap.mako" />
<%def name="title()">Account Information: ${user.username}</%def>
<%namespace file="func.mako" import="account_nav"/>

${account_nav()}

<div class="account_group">
    <ul>
        <li>${user.username}</li>
        <li>${user.name}</li>
        <li>${user.email}</li>
        <li>${user.signup}</li>
        <li>${user.last_login}</li>
    </ul>
</div>

<div class="account_group">
    <a href="" id="show_key">View API Key</a>
    <div id="api_key" style="display: none;"></div>
</div>

<div class="account_group">
    <a href="#" id="show_password">Reset Password</a>
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
                    <input type="button" id="submit_password_change" value="Change" />
                </li>
            </ul>
        </form>
    </div>
    <div id="password_msg"></div>
</div>

<%def name="add_js()">
    <script type="text/javascript">
        $(document).ready(function() {
            bookie.accounts.init();
        });
    </script>
</%def>
