<%def name="bmark_block(bmark)">
    <div class="yui3-u-1">
        <div class="yui3-g bmark">
            <div class="yui3-u-1-8">${bmark.stored.strftime("%m/%d")}</div>
            <div class="yui3-u-3-4">
                <a href="${bmark.url}">${bmark.description}</a>
            </div>
            <div class="yui3-u-1-8">
                <input type="checkbox"></input>
                <input type="checkbox"></input>
            </div>

            <div class="yui3-u-1-8">&nbsp;</div>
            <div class="yui3-u-3-4">
                % for tag in bmark.tags:
                    ${tag}
                %endfor
            </div>
            <div class="yui3-u-1-8">${bmark.stored.strftime('%H:%M%P')}</div>
        </div>
    </div>
</%def>
