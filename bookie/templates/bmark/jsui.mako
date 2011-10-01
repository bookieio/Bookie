<%inherit file="/main_wrap.mako" />
<%def name="title()">Recent JS Bookmarks</%def>

<h1></h1>

<!-- Show the tag filter ui -->
<%
    if tags:
        url = 'bmark_recent_tags'
    else:
        url = 'bmark_recent'

    if username:
        url = 'user_' + url

%>
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

    <div class="description">
            <a href="/redirect/${'<%= hash_id %>'|n}"
               title="${'<%= extended %>'|n}">${'<%= description %>'|n}</a>
    </div>
    <div class="dateinfo" title="${'<%= prettystored %>'|n}">${'<%= dateinfo %>'|n}</div>

    <div class="url" title="${'<%= url %>'|n}">
        ${'<%= url %>'|n}
    </div>
    <div class="actions">
        <span class="item">
            <a href="/bmark/readable/${'<%= hash_id %>'|n}"
               title="Readable"
            class="button">R</a>
        </span>
    </div>
</script>
