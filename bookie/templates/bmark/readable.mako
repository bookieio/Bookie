<%inherit file="/main_wrap.mako" />
<%def name="title()">Displaying: ${bmark.url}</%def>
<h1>Displaying: ${bmark.url}</h1>

<div>
    % if bmark.readable:
        ${bmark.readable.content}
    % else:
        <p>No parsed content for this bookmark</p>
    % endif
</div>
