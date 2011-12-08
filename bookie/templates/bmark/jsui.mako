<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="bmarknextprev, tag_filter"/>
<%def name="title()">Recent JS Bookmarks</%def>


<!-- Show the tag filter ui -->
<%
    if tags:
        url = 'bmark_recent_tags'
    else:
        url = 'bmark_recent'

    api_key = None

    if request.user.username:
        username = request.user.username
        url = 'user_' + url
        api_key = request.user.api_key

%>

<div class="controls">
    <div class="">
        <div class="" style="float: right;">

            <span class="page_info">Showing <span class="count"></span> bookmarks</span>
            <span class="buttons paging">
            </span>
        </div>

        % if username is not None:
            <div class="buttons" style="display: inline-block; width: 10em; vertical-align: middle;">
                   <a href="${request.route_url('user_bmark_new', username=username)}"
                       class="button">
                       <span class="icon">&</span> Add Bookmark
                   </a>
            </div>
        % endif
        <div class="tag_filter_container" style="">
            <select data-placeholder="Filter results by tag..."
                    style="width: 500px;"
                    multiple=""
                    class="chzn-select"
                    tabindex="-1" id="tag_filter">
                    <option value=""></option>
                    <option>American Black Bear</option>
                    <option>Asiatic Black Bear</option>
                    <option>Brown Bear</option>
                    <option>Giant Panda</option>
                    <option selected="">Sloth Bear</option>
                    <option disabled="">Sun Bear</option>
                    <option selected="">Polar Bear</option>
                    <option disabled="">Spectacled Bear</option>
            </select>
        </div>
    </div>
</div>

<div class="data_list">
</div>

<div class="controls">
    <div class="yui3-g">
        <div class="yui3-u-1-2">
        </div>

        <div class="yui3-u-1-2" style="text-align: right;">
            <span class="buttons paging">
            </span>
        </div>
    </div>
</div>

<%include file="../jstpl.mako"/>

<%def name="add_js()">
    <script type="text/javascript">
        // Create a new YUI instance and populate it with the required modules.
        YUI().use('node', 'console', 'bookie-model', 'bookie-api',
            'bookie-view',  function (Y) {

            var username = undefined,
                api_cfg = {
                    url: '/api/v1'
                };
            % if username:
                username = '${username}';
                api_cfg.route = 'bmarks_all';
                api_cfg.api_key = ${request.user.api_key};
            % else:
                api_cfg.route = 'bmarks_all';
                api_cfg.username = null;
            % endif

            var api = new Y.bookie.Api(api_cfg);

            api.call({
                'success': function (data, request) {
                    // build models out of our data
                    var models = new Y.bookie.BmarkList();
                    models.add(Y.Array.map(
                        data.bmarks, function (bmark){
                            return new Y.bookie.Bmark(bmark);
                        })
                    );

                    models.each(function (m, i) {
                        var testview = new Y.bookie.BmarkView({
                            model: m,
                            current_user: username
                            });
                        Y.one('.data_list').appendChild(testview.render());
                    });
                }
            });


        });
    </script>

</%def>
