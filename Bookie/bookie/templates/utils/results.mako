<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev"/>

<h2>Found ${result_count} results for ${phrase}:</h2>
<div class="yui3-g data_list">
    ${display_bmark_list(search_results)}
</div>
