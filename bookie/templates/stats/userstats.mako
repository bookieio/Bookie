<%inherit file="/main_wrap.mako" />
<%def name="title()">Recent Bookmarks</%def>
<%def name="header()">
</%def>
<div class="bmarks"></div>
<%include file="../jstpl.mako"/>
<p>Bookmark count stats for ${request.user.username}</p>
<input type="date" id="start_date">
<input type="date" id="end_date">
<button id="show_graph">Click</button>
<div id="bmark_count_graph"></div>
<%def name="add_js()">
    <script type="text/javascript">
        // Create a new YUI instance and populate it with the required modules.
        YUI().use('bookie-view', 'charts', function (Y) {
            Y.on('domready', function() {
                var api_cfg = {
                    url: APP_URL + '/api/v1',
                    username: '${request.user.username}',
                    api_key: '${request.user.api_key}',
                },
                user_stats_view = new Y.bookie.UserBmarkCountView({
                    api_cfg: api_cfg
                });
                user_stats_view.render();
            });
        });
    </script>
</%def>
