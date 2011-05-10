<%def name="display_popular_bmarks(bmark_list)">
    <%
        from datetime import datetime
        current_date = datetime(1900, 1, 1).strftime("%m/%d")
        last_date = current_date
    %>
    <div class="yui3-g">
        % for hashed in bmark_list:
            ${bmark_block(hashed.bmark[0], last_date)}
            <%
                last_date = hashed.bmark[0].stored.strftime("%m/%d")
            %>

        % endfor
    </div>


</%def>

<%def name="display_bmark_list(bmark_list)">
    <%
        from datetime import datetime
        current_date = datetime(1900, 1, 1).strftime("%m/%d")
        last_date = current_date
    %>
    <div class="yui3-g">
        % for bmark in bmark_list:
            ${bmark_block(bmark, last_date)}
            <%
                last_date = bmark.stored.strftime("%m/%d")
            %>

        % endfor
    </div>
</%def>

<%def name="bmark_block(bmark, last_date)">
    <%
        is_new = (last_date != bmark.stored.strftime("%m/%d"))
    %>
    <div class="yui3-u-1"
         % if is_new:
             style="border-top: 1px solid #999999;"
         % endif
         class="bmark_block"
    >
        <div class="yui3-g bmark">
            <div class="yui3-u-1-8">
                <div class="center">
                    % if is_new:
                        ${date_divider(bmark.stored)}
                    % endif
                </div>
            </div>

            <div class="yui3-u-7-8">
                <div class="yui3-g">
                    <div class="yui3-u-7-8">
                        <a class="bmark" href="${request.route_url('redirect', hash_id=bmark.hash_id)}" title="${bmark.extended}">${bmark.description}</a>
                    </div>

                    <div class="yui3-u-1-8 actions col_end">
                            <span class="item">
                                <a href="${request.route_url('bmark_readable',
                                hash_id=bmark.hash_id)}" title="Readable"
                                class="button"> R </a>
                            </span>
                        % if allow_edit:
                            <span class="item"><a href="#" title="Edit"
                            class="button"> E </a></span>
                            <span class="item"><a
                            href="${request.route_url('bmark_confirm_delete',
                            bid=bmark.bid)}" title="Delete" class="button"> X </a></span>
                        % endif
                    </div>

                    <div class="yui3-u-7-8">
                        <div class="tags">
                            % for tag in bmark.tags:
                                <a class="tag"
                                href="${request.route_url('tag_bmarks', tags=[tag], page=prev)}">${tag}</a>
                            % endfor
                        </div>
                    </div>

                    <div class="yui3-u-1-8">
                        <div>&nbsp;</div>
                    </div>
                </div>
            </div>
        </div>

    </div>
</%def>

<%def name="date_divider(dateobj)">
    <div class="calendar" title=" ${dateobj.strftime("%m/%d/%Y")} ">
        <h2>${dateobj.strftime("%b")}</h2>
        <div>${dateobj.strftime("%d")}</div>
    </div>
</%def>

<%def name="bmarknextprev(page, max_count, count, next_url, url_params=None, tags=None)">
    <%
        if max_count == count:
            show_next = True
        else:
            show_next = False


        if url_params is None:
            url_params = {}

        prev = page - 1
        next = page + 1
    %>

    % if page != 0:
        <a href="${request.route_url(next_url, tags=tags, **url_params)}?page=${prev}"
           class="button">Prev</a>
    % endif

    % if show_next:
        <a href="${request.route_url(next_url, tags=tags, **url_params)}?page=${next}"
           class="button">Next</a>
    % endif

</%def>

<%def name="tag_filter(tags=None)">
        <div class="tag_filter">
            <form id="filter_form" name="filter_form"
                action="${request.route_url('bmark_recent')}" method="GET">
                <span class="title">Tags&nbsp;</span>
                <input type="input" name="tag_filter" id="tag_filter"
                       placeholder="enter tags.."

                      % if tags:
                          value="${" ".join(tags)}"
                      % endif
                />
                <input type="submit" name="filter" value="Go" />
            </form>
        </div>
</%def>

<%def name="search_form(terms=None, with_content=False)">
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
