<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="api_setup, pager_setup"/>
<%def name="title()">Search results for: ${phrase}</%def>

<div class="bmarks"></div>
<%include file="../jstpl.mako"/>

<%def name="add_js()">
    <script type="text/javascript">
        // Create a new YUI instance and populate it with the required modules.
        YUI().use('node', 'console', 'bookie-view', 'bookie-model',
            'bookie-history-module', function (Y) {
            <%
                # we might have a user from the resource path that we want to keep tabs on
                resource_username = username if username else False
            %>

            ${api_setup(request.user)}

            % if username:
                var resource_username = '${username}';
            % else:
                var resource_username = undefined;
            % endif

            % if count or page:
                ${pager_setup(count=count, page=page)}
            % endif

            // we want to call the all url route for this view
            listview = new Y.bookie.SearchingBmarkListView({
                api_cfg: api_cfg,
                current_user: username,
                resource_user: resource_username,
                phrase: '${phrase}'.split(' ')
            });

            if (pager) {
                listview.set('pager', pager);
            }

            if ('${phrase}' !== '') {
                listview.api.set('phrase', '${phrase}'.split(' '));
            } else {
                tags = [];
            }

            // bind up the history tracker
            var hist = new Y.bookie.BmarkListHistory({
                pager: pager,
                terms: '${phrase}'.split(' '),
                route: '/results'
            });
            Y.one('.bmarks').appendChild(listview.render());

            var tagcontrol = new Y.bookie.TagControl({
               api_cfg: api_cfg,
               srcNode: Y.one('#tag_filter'),
               initial_tags: '${phrase}'.split(' '),
            });
            tagcontrol.render();

        });
    </script>
</%def>
