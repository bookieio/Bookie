<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="bmark_block"/>
<%def name="title()">Recent Bookmarks</%def>

<h1>Showing ${count} bookmarks</h1>

<div class="yui3-g data_list">
    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8">
        % if page != 0:
        <% prev = page - 1 %>
            <a href="${route_url('bmark_recent_page', page=prev)}">Prev</a>
        % endif
        <% next = page + 1%>
        <a href="${route_url('bmark_recent_page', page=next)}">Next</a>
    </div>

    % for mark in bmarks:
        ${bmark_block(mark)}
    % endfor

    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8">
        % if page != 0:
        <% prev = page - 1 %>
            <a href="${route_url('bmark_recent_page', page=prev)}">Prev</a>
        % endif
        <% next = page + 1%>
        <a href="${route_url('bmark_recent_page', page=next)}">Next</a>
    </div>
</div>
