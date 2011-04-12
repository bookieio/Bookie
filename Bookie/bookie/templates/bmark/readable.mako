<%inherit file="/main_wrap.mako" />
<%def name="title()">Displaying: ${bmark.url}</%def>
<h1>Displaying: ${bmark.url}</h1>

<div>
    ${bmark.readable.content}
</div>
