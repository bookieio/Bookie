<%inherit file="/main_wrap.mako" />
<%def name="title()">Displaying: ${bmark.url}</%def>

<h1>Displaying: <a class="bmark"
                % if username:
                    href="${request.route_url('user_redirect', hash_id=bmark.hash_id, username=username)}">${bmark.bmark[0].description}</a></h1>
                % else:
                    href="${request.route_url('redirect', hash_id=bmark.hash_id)}">
                % endif
                ${bmark.bmark[0].description}</a></h1>
<div id="readable_content">
    % if bmark.readable and bmark.readable.content:
        ${bmark.readable.content|n}
    % else:
        <p>No parsed content for this bookmark</p>
    % endif
</div>
