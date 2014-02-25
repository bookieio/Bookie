<%inherit file="/main_wrap.mako" />
<div class="readable">
    <%def name="title()">Displaying: 
        % if bmark.description:
            ${bmark.description}
        % else:
            ${bmark.hashed.url}
        % endif
    </%def>

    <h1>Displaying: <a class="bmark"
                    % if username:
                        href="${request.route_url('user_redirect', hash_id=bmark.hash_id, username=username)}">${bmark.description}</a></h1>
                    % else:
                        href="${request.route_url('redirect', hash_id=bmark.hash_id)}">
                    % endif
                    ${bmark.description}</a></h1>
    <div id="readable_content">
        % if bmark.readable and bmark.readable.content:
            ${bmark.readable.content|n}
        % else:
            <p>No parsed content for this bookmark</p>
        % endif
    </div>
</div>
