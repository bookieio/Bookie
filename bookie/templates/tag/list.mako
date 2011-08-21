<%inherit file="/main_wrap.mako" />
<%def name="title()">Your Tags</%def>

<h1>${tag_count} Tags</h1>
<div class="yui3-g data_list">
% for tag in tag_list:
    <div class="yui3-u-1">
        % if username:
            <a href="${request.route_url('user_tag_bmarks', tags=[tag.name],
                        username=username)}">${tag.name}</a>
        % else:
            <a href="${request.route_url('tag_bmarks', tags=[tag.name])}">${tag.name}</a>
        % endif
    </div>
% endfor
</div>
