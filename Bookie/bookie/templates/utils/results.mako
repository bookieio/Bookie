<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev"/>
<%def name="title()">Search results for: ${phrase}</%def>

<h2>Found ${result_count} results for ${phrase}:</h2>
<div class="yui3-g data_list">
    ${display_bmark_list(search_results)}
</div>
