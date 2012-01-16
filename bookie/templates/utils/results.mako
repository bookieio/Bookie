<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev"/>
<%
    url = 'search_results_rest'
    if username:
        url = 'user_' + url
    url_params = {
        'terms': phrase
    }
%>
<div class="yui3-g data_list">
    <div class="yui3-u-2-3">&nbsp;</div>
    <div class="yui3-u-1-3 col_end">Showing ${count} bookmarks</div>

    <div class="yui3-u-7-8 buttons">
        &nbsp;
    </div>
    <div class="yui3-u-1-8 col_end buttons">
        ${bmarknextprev(page, max_count, count, url, username=username, url_params=url_params)}
    </div>
    <div class="yui3-u-1 data_body">
        ${display_bmark_list(search_results, username=username)}
    </div>
</div>
