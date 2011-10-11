<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="bmarknextprev, tag_filter"/>
<%def name="title()">Recent JS Bookmarks</%def>


<!-- Show the tag filter ui -->
<%
    if tags:
        url = 'bmark_recent_tags'
    else:
        url = 'bmark_recent'

    if username:
        url = 'user_' + url

%>

<div class="controls">
    <div class="">
        <div class="" style="float: right;">

            <span class="page_info">Showing <span class="count"></span> bookmarks</span>
            <span class="buttons paging">
            </span>
        </div>

        <div class="buttons" style="display: inline-block; width: 10em; vertical-align: middle;">
            % if username is not None:
               <a href="${request.route_url('user_bmark_new', username=username)}"
                   class="button">
                   <span class="icon">&</span> Add Bookmark
               </a>
            % endif
        </div>
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

<script type="text/template" id="bmark_row">
    <div class="tags">
        ${'<% _.each(tags, function (tag) { %>'|n}
            <a class="tag"
                href="/tags/${'<%= tag.name %>'|n}">${'<%= tag.name %>'|n}</a>
        ${'<% }); %>'|n}
    </div>

    <div class="description">
            <a href="/redirect/${'<%= hash_id %>'|n}"
               title="${'<%= extended %>'|n}">${'<%= description %>'|n}</a>
    </div>
    <div class="actions">
       <span class="icon" title="${'<%= prettystored %>'|n}">\</span>
        % if username is not None:
            <a href="/${username}/edit/${'<%= hash_id %>'|n}"
               title="Edit the bookmark" alt="Edit the bookmark"
               class="edit">
               <span class="icon">p</span>
           </a>

            <a href="#" title="Delete the bookmark" alt="Delete the bookmark"
               class="delete">
               <span class="icon">*</span>
           </a>
        % endif
    </div>

    <div class="url" title="${'<%= url %>'|n}">
        <a href="/bmark/readable/${'<%= hash_id %>'|n}"
           title="View readable content" alt="View readable content">
            <span class="icon">E</span>
        </a> ${'<%= url %>'|n}
    </div>
</script>

<script type="text/template" id="previous_control">
    <a href="#" class="button previous"><span class="icon">[</span> Prev</a>
</script>

<script type="text/template" id="next_control">
    <a href="#" class="button next">Next <span class="icon">]</span></a>
</script>

<%def name="add_js()">
    <script data-main="/static/js/" src="/static/js/lib/require.js"></script>
    <script type="text/javascript" src="/static/js/lib/backbone-min.js"></script>
    <script type="text/javascript" src="/static/js/lib/history.js"></script>
    <script type="text/javascript" src="/static/js/lib/chosen.jquery.min.js"></script>

    <script type="text/javascript">
        require(["bookie/ui", "bookie/api"], function(ui, api) {
            // update the api to say hey, we should use a username/not in our
            // calls
            var username = undefined;
            % if username:
                username = '${username}';
                api.init(APP_URL, username);
            % else:
                api.init(APP_URL);
            % endif

            // do the api call to get the most recent bookmarks
            var page_control = new ui.Control({'page': ${page},
                                                      'count': ${count}}),
                cview = new ui.ControlView({
                                'el': $('.controls'),
                                'model': page_control,
                                'username': username});
            ui.filterui.init();
        });

    </script>
</%def>
