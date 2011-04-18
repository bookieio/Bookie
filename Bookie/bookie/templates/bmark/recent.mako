<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="display_bmark_list, bmarknextprev, tag_filter"/>
<%def name="title()">Recent Bookmarks</%def>

<h1></h1>

<!-- Show the tag filter ui -->

<div class="yui3-g data_list">
    <div class="yui3-u-1-2">
        ${tag_filter()}
    </div>
    <div class="yui3-u-1-2 col_end">Showing ${max_count} bookmarks</div>

    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8 col_end">
        ${bmarknextprev(page, max_count, count, 'bmark_recent_page')}
    </div>

    <div class="yui3-u-1">
        ${display_bmark_list(bmarks)}
    </div>

    <div class="yui3-u-7-8">&nbsp;</div>

    <div class="yui3-u-1-8 col_end">
        ${bmarknextprev(page, max_count, count, 'bmark_recent_page')}
    </div>
</div>
