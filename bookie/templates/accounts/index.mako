<%inherit file="/main_wrap.mako" />
<%def name="title()">Account Information: ${user.username}</%def>
<%namespace file="func.mako" import="account_nav, password_reset"/>
<%
    date_fmt = "%m/%d/%Y"
%>
${account_nav()}

<div class="form yui3-g">
    <div class="yui3-u-1-4">
        <div class="heading">${user.username}</div>

        <div>Member since: <span>
                        % if user.signup:
                            ${user.signup.strftime(date_fmt)}
                        % else:
                            Unknown
                        % endif
                </span>
        </div>
        <div>
            Last Seen: <span>${user.last_login.strftime(date_fmt)}</span>
        </div>
    </div>
    <div class="yui3-u-3-4">
        <form>
            <ul>
                <li>
                    <label>Name</label>
                    <input type="text" id="name" name="name" value="${user.name}" />
                </li>
                <li>
                    <label>Email</label>
                    <input type="text" id="email" name="email" value="${user.email}" />
                </li>
                <li>
                    <label></label>
                    <input type="button" id="submit_account_change" value="Update" class="button" />
                </li>

            </ul>
        </form>
        <div id="account_msg" class="error"></div>
    </div>
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

${password_reset(reset=False)}

<%def name="add_js()">
    <script type="text/javascript">
        $(document).ready(function() {
            bookie.accounts.init();
        });
    </script>
</%def>
