<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="api_setup"/>
<%def name="title()">${"Add" if bmark and bmark.hashed.url == "" else "Edit"} bookmark</%def>
<%
    # we might have a user from the resource path that we want to keep tabs on
    resource_username = username if username else False

    if request.user and request.user.username:
        auth_username = request.user.username
        api_key = request.user.api_key
    else:
        auth_username = None
        api_key = None
%>
<div class="yui3-g">
    <div class="yui3-u-1">
    <form
        % if new:
            action="${request.route_url('user_bmark_new_error', username=request.user.username)}"
        % else:
            action="${request.route_url('user_bmark_edit_error', username=request.user.username, hash_id=bmark.hash_id)}"
        % endif
        method="post" class="login form">
        <div class="heading">
            % if bmark and bmark.hashed.url == "":
                Add
            % elif bmark.is_private:
                <div style="background-color: #ff4040;">
                    Edit <span aria-hidden="true" class="icon icon-lock" title="Private Bookmark"></span> private bookmark
                </div>
            % else:
                Edit bookmark
            % endif
        </div>
        % if message:
            <p class="error">${message}</p>
        % endif
        <ul>
            <li>
                <label>Url</label>
                % if new:
                    <input id="url" type="url" name="url" value="${bmark.hashed.url}"
                        placeholder="url of website..."/>
                % else:
                    <input type="hidden" name="url" value="${bmark.hashed.url}"
                        placeholder="url of website..."/>
                    <div class="url">
                        <a href="${bmark.hashed.url}">${bmark.hashed.url}</a>
                    </div>
                % endif
            </li>
            <li>
                <label>Description</label>
                <input type="text" name="description"
                       value="${bmark.description if bmark.description else ''}"
                       placeholder="description..."/>
            </li>
            <li class="form_tags">
                <label>Tags</label>
                <input type="text" id="tags" name="tags"
                       value="${bmark.tag_str if bmark.tag_str else ''}"
                       placeholder="add tags..."/>
            </li>

            % if tag_suggest and len(tag_suggest) > 0:
                <li>
                    <label></label>
                    <span id="tag_suggest">Suggested Tags:
                    % for tag in tag_suggest:
                        <a href="" class="prev_tag">${tag}</a>
                    % endfor
                    </span>
                </li>
            % endif

            <li>
                <label>Extended</label>
                <input type="text" name="extended"
                       value="${bmark.extended if bmark.extended else ''}"
                       placeholder="extended description..."/>
            </li>

            <li>
                <label>Private</label>
                % if new or not bmark.is_private:
                    <input type="checkbox" name="is_private" />
                % else:
                    <input type="checkbox" name="is_private" checked="checked" />
                % endif
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
    <div id="readable_content" style="display: none;"></div>
    </div>
</div>

<%include file="../jstpl.mako"/>
<%def name="add_js()">
    <script type="text/javascript">
        // Create a new YUI instance and populate it with the required modules.
        YUI().use('node', 'console', 'bookie-view', 'bookie-readable', 'bookie-indicator',  function (Y) {
            ${api_setup(request.user)}
            var tagcontrol = new Y.bookie.TagControl({
               api_cfg: api_cfg,
               'srcNode': Y.one('#tags'),
               'with_submit': false
            });
            tagcontrol.render();
            var bmark_edit_view = new Y.bookie.BmarkEditView();

            // Watch the form for the submit event and make sure that the tag
            // control is up to date before we submit the form.
            Y.one('form').on('submit', function(ev) {
                // Fire the tag update event for the tag control to update
                // anything that's currently entered.
                Y.fire('tag:update', {
                    type: 'blur',
                    target: ''
                });
            });

            // so now we need to bind up the prev tags to add to our tag
            // control as well
            Y.all('.prev_tag').on('click', function (ev) {
                ev.preventDefault();
                var target = ev.currentTarget;
                Y.fire('tag:add', {
                    tag: target.get('text')
                });
                target.remove();
            });

            % if new and bmark.hashed.url:
            // Start out testing to see if we can load the readable content
            // for the url via our bookie-readable js module
            var readable_target = Y.one('#readable_content');
            readable_target.show();
            var readable = new Y.bookie.readable.Api({
                url: '${bmark.hashed.url}'
            });

            var indicator = new Y.bookie.Indicator({
                target: readable_target
            });
            indicator.render();
            indicator.show();

            readable.call({
                success: function (data, response, args) {
                    readable_target.setContent(data.readable)
                    indicator.hide();
                },

                error: function (data, status_str, response, args) {
                    console.log(data);
                    console.log(status_str);
                    console.log(response);
                    indicator.hide();
                }
            });
            % endif
        });
    </script>
</%def>
