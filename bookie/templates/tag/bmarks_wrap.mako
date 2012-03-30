<%inherit file="/main_wrap.mako" />
<%def name="title()">Bookmarks for: ${", ".join(tags)}</%def>

<div class="yui3-g data_list">
    <div class="yui3-u-1 data_body">
        include file="bmarks.mako"
    </div>
</div>
