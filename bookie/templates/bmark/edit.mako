<%inherit file="/main_wrap.mako" />
<%def name="title()">Edit bookmark</%def>

<div class="yui3-g data_list">
    <div class="yui3-u-1">
    <form action="${request.route_url('user_bmark_edit_error', username=request.user.username, hash_id=bmark.hash_id)}" method="post" class="login form bmark">
        <div class="heading">Edit Bookmark</div>
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
                <input type="text" name="description" value="${bmark.description}"
                       placeholder="description..."/>
            </li>
            <li>
                <label>Tags</label>
                <input type="text" id="tags" name="tags" value="${bmark.tag_str}"
                       placeholder="add tags..."/>
            </li>
            <li>
                <label>Extended</label>
                <input type="text" name="extended" value="${bmark.extended}"
                       placeholder="extended description..."/>
            </li>
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
