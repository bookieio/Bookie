<%inherit file="/main_wrap.mako" />
<%def name="title()">Displaying: ${bmark.url}</%def>
<h1>Displaying: <a class="bmark" href="${request.route_url('redirect',
    hash_id=bmark.hash_id)}">${bmark.bmark[0].description}</a></h1>

<div id="readable_content">
    % if bmark.readable:
        ${bmark.readable.content}
    % else:
        <p>No parsed content for this bookmark</p>
    % endif
</div>
