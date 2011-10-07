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
    <div class="yui3-g">
        <div class="yui3-u-1-2">
            <div class="buttons">
                % if username is not None:
                   <a href="${request.route_url('user_bmark_new', username=username)}"
                       class="button">
                       <span class="icon">&</span> Add Bookmark
                   </a>
                % endif
            </div>

        </div>

        <div class="yui3-u-1-2" style="text-align: right;">

            <span class="page_info">Showing <span class="count"></span> bookmarks</span>
            <span class="buttons paging">
            </span>
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
    <script type="text/javascript" src="/static/js/lib/backbone-min.js"></script>
    <script type="text/javascript" src="/static/js/lib/history.js"></script>
    <script type="text/javascript" src="/static/js/jsui.js"></script>

    <script type="text/javascript">
        $(document).ready(function() {
            // update the api to say hey, we should use a username/not in our
            // calls
            var username = undefined;
            % if username:
                username = '${username}';
                bookie.api.init(APP_URL, username);
            % else:
                bookie.api.init(APP_URL);
            % endif

            // do the api call to get the most recent bookmarks
            var page_control = new bookie.bb.Control({'page': ${page},
                                                      'count': ${count}}),
                cview = new bookie.bb.ControlView({
                                'el': $('.controls'),
                                'model': page_control,
                                'username': username});
        });
    </script>
</%def>
