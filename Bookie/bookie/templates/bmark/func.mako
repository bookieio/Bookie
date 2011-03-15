<%def name="display_bmark_list(bmark_list)">
    <%
        from datetime import datetime
        current_date = datetime.now().strftime("%m/%d")
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
                        <a href="${bmark.url}">${bmark.description}</a>
                    </div>

                    <div class="yui3-u-1-8">
                        % if allow_edit:
                            <span><a href="#">edit</a></span>
                            <span><a href="${request.route_url('bmark_delete', bid=bmark.bid)}">delete</a></span>
                        % endif
                    </div>

                    <div class="yui3-u-7-8">
                        % for tag in bmark.tags:
                            <a href="${request.route_url('tag_bmarks', tag=tag, page=prev)}">${tag}</a>
                        %endfor
                    </div>

                    <div class="yui3-u-1-8">${bmark.stored.strftime('%H:%M%P')}</div>
                </div>
            </div>
        </div>

    </div>
</%def>

<%def name="date_divider(dateobj)">
    <div class="calendar">
        <h2>${dateobj.strftime("%b")}</h2>
        <div>${dateobj.strftime("%d")}</div>
    </div>
</%def>

<%def name="bmarknextprev(page, max_count, count, next_url, url_params=None)">
    <%
        if max_count == count:
            show_next = True
        else:
            show_next = False

        next = page + 1

        if url_params is None:
            url_params = {}
    %>

    % if page != 0:
    <% prev = page - 1 %>
        <a href="${request.route_url(next_url, page=prev, **url_params)}">Prev</a>
    % endif

    % if show_next:
        <a href="${request.route_url(next_url, page=next, **url_params)}">Next</a>
    % endif

</%def>
