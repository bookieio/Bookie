<%inherit file="/wrapper.mako" />
<%def name="title()">User Accounts</%def>
<div>
    <h1>QMail User Accounts</h1>
    <div class="content_body">
        <p>
            <span id="new_user" class="yui-button yui-link-button">
                <em class="first-child">
                    <a href="${h.url(controller='accounts', action='new')}"
                    id="new_user_button" class="add">New User</a>
                </em>
            </span>
        </p>
        <table cellspacing="0" cellpadding="0" border="0" width="" class="zebra data">
            <thead>
                <tr>
                    <th>ID</th>
                    <th width="80%">Username</th>
                    <th>Controls</th>
                </tr>
            </thead>
            <tbody>
                % for u in c.user_list:
                    <tr>
                        <td class="center">${u.user_id}</td>
                        <td width="80%">${u.user_name}</td>
                        <td class="center">
                            <span class="edit">
                            ${h.link_to('Edit', h.url('/accounts/{0}/edit'.format(u.user_name)),
                                    class_="qp_button mor_user_edit")}
                            </span>
                            <span class="delete">
                            ${h.link_to('Delete', h.url('/accounts/{0}/delete'.format(u.user_name)),
                                    class_="qp_button mor_user_delete")}
                            </span>
                        </td>
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>
<p class="clear">&nbsp;</p>
<%def name="add_js()">
    <script type="text/javascript">
        YUI({
            debug: true

        }).use('qadmin', function (Y) {
            win = new Y.QAdmin.Window();
            win.account_list.init();
        });
    </script>
</%def>
