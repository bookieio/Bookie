<%inherit file="/wrapper.mako" />
<%def name="title()">Create New User</%def>
<h2>Create New User Account</h2>
<div class="content_body">
    <div id="edit_form" class="form">

        <div class="form">
        <fieldset>
            <!--<div class="fieldset_legend">Edit User Account</div>-->
            %if c.form_errors:
                <div class="error"> Please correct the errors listed below </div>
            %endif

            ${h.form(h.url(controller='accounts', action='new_errors'), id="form1")}
            <ol class="form">

                <li formfield="user_name">
                    <label for="user_name">User Name</label>
                    ${h.text('user_name',
                            id="user_name",
                            class_="form",
                    )}
                </li>
                <li>
                    <a href="#" id="qp_ldap_search" class="qp_button">Lookup LDAP User</a>
                </li>

                <li formfield="is_ldap">
                    <label for="is_ldap">Is LDAP User</label>
                    ${h.checkbox('is_ldap', id='is_ldap', value=1, checked=False, disabled=True)}
                </li>

                <li formfield="groups">
                    <label for="groups">Groups</label>
                    <div class="multiplecheckbox">
                        % for g in c.group_list:
                            ${h.checkbox('groups', value=g.group_name, checked=False)} - ${g.group_name.upper()}
                            <br />
                        % endfor
                    </div>

                    <span class="form helptext">Select the groups this user
                    belongs</span>
                </li>
                <li formfield="submit">
                    ${h.submit('submit', id="submit", value="Add User", class_="form")}
                </li>
            </ol>
        </fieldset>
        ${h.end_form()}
        </div>
    </div>
    <p>&nbsp;</p>
    <div style="clear:both;">&nbsp;</div>
</div>

<%def name="add_js()">
    <script type="text/javascript">
        YUI({
            debug: true

        }).use('qadmin', function (Y) {
            win = new Y.QAdmin.Window();
            win.account_new.init();
        });
    </script> 
</%def>
