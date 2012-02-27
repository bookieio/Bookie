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
        YUI().use('bookie-api', 'bookie-history', 'bookie-model',
            'bookie-tagcontrol', 'bookie-view', function (Y) {
            <%
                # we might have a user from the resource path that we want to keep tabs on
                resource_username = username if username else False
            %>

            ${api_setup(request.user)}

            % if username:
                var resource_username = '${username}';
                var route = '/recent/' + resource_username;
            % else:
                var resource_username = undefined;
                var route = '/recent'
            % endif

            % if count or page:
                ${pager_setup(count=count, page=page)}
            % endif

            // we want to call the all url route for this view
            listview = new Y.bookie.TagControlBmarkListView({
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
            } else {
                tags = [];
            }

            // bind up the history tracker
            var hist = new Y.bookie.BmarkListHistory({
                pager: pager,
                terms: tags,
                route: route
            });

            Y.one('.bmarks').appendChild(listview.render());
            var tagcontrol = new Y.bookie.TagControl({
               api_cfg: api_cfg,
               srcNode: Y.one('#tag_filter'),
               initial_tags: tags
            });
            tagcontrol.render();
        });
    </script>
</%def>
