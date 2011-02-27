<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="bmark_block"/>
<%def name="title()">Bookmarks for: ${tag}</%def>

<h1>Bookmarks: ${tag}</h1>

<div class="yui3-g data_list">
    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8">
        % if page != 0:
        <% prev = page - 1 %>
            <a href="${route_url('tag_bmarks_page', tag=tag, page=prev)}">Prev</a>
        % endif
        <% next = page + 1%>
        <a href="${route_url('tag_bmarks_page', tag=tag,  page=next)}">Next</a>
    </div>

    % for mark in bmark_list:
        ${bmark_block(mark)}
    % endfor

    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8">
        % if page != 0:
        <% prev = page - 1 %>
            <a href="${route_url('tag_bmarks_page', tag=tag, page=prev)}">Prev</a>
        % endif
        <% next = page + 1%>
        <a href="${route_url('tag_bmarks_page', tag=tag, page=next)}">Next</a>
    </div>
</div>
