<%inherit file="/main_wrap.mako" />
<%def name="title()">Recent Bookmarks</%def>
<%def name="header()">
</%def>
<style>
#mychart {
    margin-left: 50px;
    width: 1000px;
    height: 500px;
}
</style>
<div class="bmarks"></div>
<%include file="../jstpl.mako"/>
<p>Bookmark count stats for ${request.user.username}</p>
<span id="user_stats"></span>
<div id="mychart"></div>
<%def name="add_js()">
<%
import json
%>
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


