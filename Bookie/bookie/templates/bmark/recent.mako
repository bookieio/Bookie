<%inherit file="/main_wrap.mako" />
<%namespace file="func.mako" import="display_bmark_list, bmarknextprev"/>
<%def name="title()">Recent Bookmarks</%def>

<h1></h1>

<!-- Show the tag filter ui -->

<div class="yui3-g data_list">
    <div class="yui3-u-1-2">
        <div class="tag_filter">
            <span class="title">Filter Tags&nbsp;</span>
            <span class="item"><a href="" title="Remove tag">sports x</a></span>
            <input type="input" name="tag_filter" id="tag_filter" placeholder="enter tag.."/>
        </div>
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
