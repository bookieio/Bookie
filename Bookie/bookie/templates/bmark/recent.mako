<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="bmark_block"/>
<%def name="title()">Recent Bookmarks</%def>

<h1>Showing ${count} bookmarks</h1>

<div class="yui3-g data_list">
% for mark in bmarks:
    ${bmark_block(mark)}
% endfor
</div>
