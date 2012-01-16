<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="api_setup, pager_setup"/>
<%def name="title()">Recent Bookmarks</%def>

<div class="bmarks"></div>
<%include file="../jstpl.mako"/>

<%def name="add_js()">
<%
import json
%>
    <script type="text/javascript">
        // Create a new YUI instance and populate it with the required modules.
        YUI().use('node', 'console', 'bookie-view', 'bookie-model',  function (Y) {

            <%
                # we might have a user from the resource path that we want to keep tabs on
                resource_username = username if username else False
            %>

            ${api_setup(request.user)}

            % if username:
                resource_username = '${username}';
            % else:
                resource_username = undefined;
            % endif

            % if count or page:
                ${pager_setup(count=count, page=page)}
            % endif

            // we want to call the all url route for this view
            listview = new Y.bookie.BmarkListView({
                api_cfg: api_cfg,
                current_user: username,
                resource_user: resource_username
            });

            if (pager) {
                listview.set('pager', pager);
            }

            // pre-seed the tags list to the listview
            var tags = ${json.dumps(tags)|n};
            if (tags) {
                listview.api.set('tags', tags);
            }

            Y.one('.bmarks').appendChild(listview.render());
            var tagcontrol = new Y.bookie.TagControl({
               api_cfg: api_cfg,
               srcNode: Y.one('#tag_filter'),
               tags: tags
            });
            tagcontrol.render();
        });
    </script>
</%def>
