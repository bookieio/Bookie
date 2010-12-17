<%inherit file="/wrapper.mako" />
<%def name="title()">Edit User: ${c.user.user_name}</%def>

<h2>Edit User Account: ${c.user.user_name}</h2>

<div class="content_body">
    <div id="edit_form" class="form">

        <div class="form">

        ${h.form(h.url(controller='accounts', action='edit_error'), id="form1")}
        <fieldset>
            <!--<div class="fieldset_legend">Edit User Account</div>-->
            %if c.form_errors:
                <div class="error"> Please correct the errors listed below </div>
            %endif

            <ol class="form">

                <li formfield="user_name" style="display: none;">
                    <label for="user_name">User Name</label>
                    ${h.hidden('user_name',
                            id="user_name",
                            class_="form",
                            value=c.user.user_name,
                    )}
                </li>

                <li formfield="user">
                    <label for="user">User Name</label>
                    ${c.user.user_name}
                </li>

                <li formfield="is_ldap">
                    <label for="is_ldap">LDAP User</label>
                    ${h.checkbox('is_ldap', checked=c.user.is_ldap, disabled=True)}
                </li>

                <li formfield="groups">
                    <label for="groups">Groups</label>
                    <div class="multiplecheckbox">
                        % for g in c.group_list:
                            <%
                                in_group = False
                                if g in c.user.groups:
                                    in_group = True
                            %>
                            ${h.checkbox('groups', value=g.group_name, checked=in_group)} - ${g.group_name.upper()}
                            <br />
                        % endfor
                    </div>

                    <span class="form helptext">Select the groups this user
                    belongs</span>
                </li>
                <li formfield="submit">
                    ${h.submit('submit', id="submit", value="Edit User", class_="form")}
                </li>
            </ol>
        </fieldset>
        ${h.end_form()}
        </div>
    </div>
    <p>&nbsp;</p>
<%def name="add_js()">
    <script type="text/javascript">
        YUI({
            debug: true

        }).use('qadmin', function (Y) {
            win = new Y.QAdmin.Window();
            win.account_edit.init();
        });
    </script> 
    
</%def>
