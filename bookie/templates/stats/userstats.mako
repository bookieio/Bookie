<%inherit file="/main_wrap.mako" />
<%def name="title()">Bookmark Stats</%def>
<%def name="header()">
</%def>
<div class="bmarks"></div>
<%include file="../jstpl.mako"/>
<%namespace file="../accounts/func.mako" import="account_nav"/>
${account_nav()}
<div class="yui3-g">
    <div class="yui3-u-1">
        <div class="form">
            <div id="userstats_msg" class="error"></div>
            <div id="calendar"></div>
            <div id="bmark_count_graph"></div>
            <%def name="add_js()">
                <script type="text/javascript">
                    // Create a new YUI instance and populate it with the required modules.
                    YUI().use('bookie-view', 'calendar', 'charts', 'datatype-date', function (Y) {
                        Y.on('domready', function() {
                            var api_cfg = {
                                url: APP_URL + '/api/v1',
                                username: '${request.user.username}',
                                api_key: '${request.user.api_key}',
                            },
                            user_stats_view = new Y.bookie.UserBmarkCountView({
                                api_cfg: api_cfg,
                                container: Y.one('body')
                            });
                            user_stats_view.render();
                        });
                    });
                </script>
            </%def>
        </div>
    </div>
</div>
