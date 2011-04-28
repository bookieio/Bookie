<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="display_popular_bmarks, bmarknextprev"/>
<%def name="title()">Popular Bookmarks</%def>

<h1>Showing ${max_count} bookmarks</h1>

<div class="yui3-g data_list">
    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8 col_end buttons">
        ${bmarknextprev(page, max_count, count, 'bmark_popular_page')}
    </div>

    <div class="yui3-u-1">
        ${display_popular_bmarks(bmarks)}
    </div>

    <div class="yui3-u-7-8">&nbsp;</div>

    <div class="yui3-u-1-8 col_end buttons">
        ${bmarknextprev(page, max_count, count, 'bmark_popular_page')}
    </div>
</div>
