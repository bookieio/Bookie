<%def name="search_form(terms=None, with_content=False, username=None)">
        <div class="tag_filter">
            <form id="search_form" name="search_form"
                action="${request.route_url('search_results')}" method="GET">
                <span class="title">Search</span>
                <input type="input" name="search" id="search"
                       placeholder="enter keywords..."

                      % if terms:
                          value="${" ".join(terms)}"
                      % endif
                />

                <input type="checkbox" name="content" id="search_content"
                    % if with_content:
                        checked="checked"
                    % endif
                /> Content
                <input type="submit" name="submit" value="Go" />
            </form>
        </div>
</%def>


<%def name="api_setup(user)">
    var username = undefined,
        api_cfg = {
            url: APP_URL + '/api/v1'
        };

    % if user and user.username:
        api_cfg.api_key = '${user.api_key}';
        username = '${user.username}';
        api_cfg.username = username;
    % endif
</%def>



<%def name="pager_setup(page=0, count=50)">
    % if count:
        pager.set('count', ${count});
    % endif

    % if page:
        pager.set('page', ${page});
    % endif
</%def>


