<%inherit file="/main_wrap.mako" />
<%def name="title()">Search your bookmarks</%def>

<div class="tag_filter fullpage">
    <h2 class="title">Search</h2>
    <div class="body">
        <form
            % if username:
                action="${request.route_url('user_search_results',
                                             username=username)}"
            % else:
                action="${request.route_url('search_results')}"
            % endif
            method="get" />
            <div>
                <input type="search" name="search" id="search" placeholder="keywords.." />
                <input type="hidden" name="content" id="search_content" value="true" />
                <p>
                    <input type="checkbox" name="search_mine" id="search_mine" />
                    <label for="search_mine">Search only my bookmarks</label>
                </p>
                <input style="line-height: 1.5;" type="submit" name="submit" class="button" id="submit_search" value="Search"/>
            </div>
        </form>
    </div>

    <p>&nbsp;</p>
</div>
