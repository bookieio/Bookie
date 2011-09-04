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
<div class="yui3-g data_list">
</div>

<%def name="add_js()">
    <script type="text/javascript" src="http://documentcloud.github.com/backbone/backbone-min.js"></script>
    <script type="text/javascript" src="/static/js/jsui.js"></script>
</%def>


<script type="text/template" id="bmark_row">
    <div class="yui3-u-1 bmark_block" style="border-top: 1px solid #999999;">
        <div class="yui3-g bmark">
            <div class="yui3-u-1-8">
                <div class="center">
                </div>
            </div>

            <div class="yui3-u-7-8">
                <div class="yui3-g">
                    <div class="yui3-u-7-8">
                            <a href="/redirect/${'<%= hash_id %>'|n}"
                               title="${'<%= extended %>'|n}">${'<%= description %>'|n}</a>
                    </div>

                    <div class="yui3-u-1-8 actions col_end">
                            <span class="item">
                                <a href="/readable/${'<%= hash_id %>'|n}"
                                   title="Readable"
                                class="button">R</a>
                            </span>
                    </div>

                    <div class="yui3-u-3-8 url" title="${'<%= url %>'|n}">
                        ${'<%= url %>'|n}
                    </div>
                    <div class="yui3-u-1-2">
                        <div class="tags">
                            ${'<% _.each(tags, function (tag) { %>'|n}
                                <a class="tag"
                                    href="${'<%= tag.name %>'|n}">${'<%= tag.name %>'|n}</a>
                            ${'<% }); %>'|n}
                        </div>
                    </div>

                    <div class="yui3-u-1-8">
                        <div>&nbsp;</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</script>
