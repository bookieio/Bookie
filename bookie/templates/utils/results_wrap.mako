<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="search_form"/>
<%def name="title()">Search results for: ${phrase}</%def>

<div class="yui3-g data_list">
    <div class="yui3-u-2-3">
        ${search_form(terms=phrase.split(" "), with_content=with_content)}
    </div>
    <div class="yui3-u-1-3 col_end"></div>
    <div class="yui3-u-1 data_body">
        <%include file="results.mako"/>
    </div>
</div>
