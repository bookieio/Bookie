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
<div class="page_info">Showing <span class="count"></span> bookmarks</div>
${tag_filter(url, tags=tags, username=username)}

<div class="buttons" style="float: right;">
    ${bmarknextprev(0, 10, 10, url, tags=tags, username=username)}
</div>
<div class="buttons">
    % if username is not None:
       <a href="${request.route_url('user_bmark_new', username=username)}" class="button">+ Add</a>
    % endif
</div>

<div class="data_list">
</div>

<%def name="add_js()">
    <script type="text/javascript" src="/static/js/lib/backbone-min.js"></script>
    <script type="text/javascript" src="/static/js/jsui.js"></script>
</%def>

<script type="text/template" id="bmark_row">
    <div class="tags">
        ${'<% _.each(tags, function (tag) { %>'|n}
            <a class="tag"
                href="/tags/${'<%= tag.name %>'|n}">${'<%= tag.name %>'|n}</a>
        ${'<% }); %>'|n}
    </div>

    <div class="actions" style="width: 2em; float: left;">
        <span class="item">
            <a href="/bmark/readable/${'<%= hash_id %>'|n}"
               title="Readable"
            class="button">R</a>
        </span>
        % if username is not None:
            <span class="item">
                <a href="/${username}/edit/${'<%= hash_id %>'|n}"
                   title="Edit"
                class="button">E</a>
            </span>
        % endif
    </div>

    <div class="description">
            <a href="/redirect/${'<%= hash_id %>'|n}"
               title="${'<%= extended %>'|n}">${'<%= description %>'|n}</a>
    </div>
    <div class="dateinfo" title="${'<%= prettystored %>'|n}">${'<%= dateinfo %>'|n}</div>

    <div class="url" title="${'<%= url %>'|n}">
        ${'<%= url %>'|n}
    </div>
</script>
