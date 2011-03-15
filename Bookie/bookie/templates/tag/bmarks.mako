<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev"/>
<%def name="title()">Bookmarks for: ${tag}</%def>

<%
    url_params = {'tag': tag}
%>

<h1>Bookmarks: ${tag}</h1>

<div class="yui3-g data_list">
    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8">
        ${bmarknextprev(page, max_count, count, 'tag_bmarks_page',
                        url_params=url_params)}
    </div>

    % for mark in bmark_list:
        ${display_bmark_list(bmark_list)}
    % endfor

    <div class="yui3-u-7-8">&nbsp;</div>
    <div class="yui3-u-1-8">
        ${bmarknextprev(page, max_count, count, 'tag_bmarks_page',
                        url_params=url_params)}
    </div>
</div>
