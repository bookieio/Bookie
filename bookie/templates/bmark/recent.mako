<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="bmarknextprev, tag_filter"/>
<%def name="title()">Recent Bookmarks</%def>

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

<div class="bmarks"></div>

<%include file="../jstpl.mako"/>

<%def name="add_js()">
    <script type="text/javascript">
        // Create a new YUI instance and populate it with the required modules.
        YUI().use('node', 'console', 'bookie-view',  function (Y) {

            var username = undefined,
                api_cfg = {
                    url: APP_URL + '/api/v1'
                };

            % if request.user and request.user.username:
                api_cfg.api_key = '${request.user.api_key}';
                username = '${request.user.username}';
                api_cfg.username = username;
            % endif

            % if username:
                resource_username = '${username}';
            % else:
                resource_username = undefined;
            % endif

            % if count or page:
                var pager = new Y.bookie.PagerModel();
                % if count:
                    pager.set('count', ${count});
                % endif

                % if page:
                    pager.set('page', ${page});
                % endif
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

            Y.one('.bmarks').appendChild(listview.render());

            var tagcontrol = new Y.bookie.TagControl({
               'srcNode': Y.one('#tag_filter')
            });
            tagcontrol.render();

        });
    </script>
</%def>
