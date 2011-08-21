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
            </div>
            <div>
                <input type="checkbox" name="content" id="search_content"  /> Include Cached Content
            </div>
            <input style="line-height: 1.5;" type="submit" name="submit" class="button" id="submit_search" value="Search"/>
        </form>
    </div>

    <p>&nbsp;</p>
    <div class="note">
        <p>Search will check for terms in your bookmark tags, descriptions, and
        extended descriptions</p>
        <p>You can also check the parsed and cached versions of the pages by
        including the cached content. This will be much slower on large
        bookmark sets.</p>
    </div>
</div>
