<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="api_setup, pager_setup"/>
<%def name="title()">Search results for: ${phrase}</%def>

<div class="bmarks"></div>
<%include file="../jstpl.mako"/>

<%def name="add_js()">
    <script type="text/javascript">
        // Create a new YUI instance and populate it with the required modules.
        YUI().use('node', 'console', 'bookie-view', 'bookie-model',  function (Y) {
            // set the phrase to the input

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
            listview = new Y.bookie.SearchingBmarkListView({
                api_cfg: api_cfg,
                current_user: username,
                resource_user: resource_username,
                phrase: '${phrase}',
                with_content: ${'true' if with_content else 'false'}
            });

            if (pager) {
                listview.set('pager', pager);
            }

            Y.one('.bmarks').appendChild(listview.render());
        });
    </script>
</%def>
