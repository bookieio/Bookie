<%inherit file="/main_wrap.mako" />
<%def name="title()">${"Add" if bmark.hashed.url == "" else "Edit"} bookmark</%def>

<div class="yui3-g data_list">
    <div class="yui3-u-1">
    <form
        % if new:
            action="${request.route_url('user_bmark_new_error', username=request.user.username)}"
        % else:
            action="${request.route_url('user_bmark_edit_error', username=request.user.username, hash_id=bmark.hash_id)}"
        % endif
        method="post" class="login form bmark">
        <div class="heading">${"Add" if bmark.hashed.url == "" else "Edit"} bookmark</div>
        % if message:
            <p class="error">${message}</p>
        % endif
        <ul>
            <li>
                <label>Url</label>
                <input type="url" name="url" value="${bmark.hashed.url}"
                       placeholder="url of website..."/>
            </li>
            <li>
                <label>Description</label>
                <input type="text" name="description"
                       value="${bmark.description if bmark.description else ''}"
                       placeholder="description..."/>
            </li>
            <li>
                <label>Tags</label>
                <input type="text" id="tags" name="tags"
                       value="${bmark.tag_str if bmark.tag_str else ''}"
                       placeholder="add tags..."/>
            </li>
            <li>
                <label>Extended</label>
                <input type="text" name="extended"
                       value="${bmark.extended if bmark.extended else ''}"
                       placeholder="extended description..."/>
            </li>

            % if new and bmark.hashed.url != "":
                <li>
                    <label>Return after save</label>
                    <input type="checkbox" name="go_back"
                           checked="checked" />
                    <a title="original url" href="${bmark.hashed.url}">${bmark.description}</a>
                    <input type="hidden" name="comes_from"
                           value="${bmark.hashed.url}"
                           checked="checked" />
                </li>
            % endif
            <li>
                <label></label>
                <input type="submit" name="submit" value="Save" />
            </li>
        </ul>
    </form>
    </div>
</div>

<%def name="add_js()">
    <script type="text/javascript">
        $(document).ready(function() {
            bookie.edit.init();
        });
    </script>
</%def>
