<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev, tag_filter"/>
<h1>Bookmarks: ${", ".join(tags)}</h1>

<div class="yui3-g data_list">
    <div class="yui3-u-1-2">
    </div>
    <div class="yui3-u-1-2 col_end">Showing ${count} bookmarks</div>

    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8 col_end buttons">
        ${bmarknextprev(page, max_count, count, 'tag_bmarks',
                        tags=tags)}
    </div>

    ${display_bmark_list(bmark_list)}

    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8 col_end buttons">
        ${bmarknextprev(page, max_count, count, 'tag_bmarks',
                        tags=tags)}
    </div>
</div>
