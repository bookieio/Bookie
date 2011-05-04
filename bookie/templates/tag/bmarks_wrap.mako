<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev, tag_filter"/>
<%def name="title()">Bookmarks for: ${", ".join(tags)}</%def>

<div class="yui3-g data_list">
    <div class="yui3-u-2-3">
        ${tag_filter()}
    </div>
    <div class="yui3-u-1-3 col_end"></div>
    <div class="yui3-u-1 data_body">
        <%include file="bmarks.mako"/>
    </div>
</div>
