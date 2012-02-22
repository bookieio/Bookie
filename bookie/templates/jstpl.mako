<script type="text/template" id="bmark_row">
    <div class="tags">
        {{#each tags}}
            <a class="tag" href="">{{name}}</a>
        {{/each}}
    </div>

    <div class="description">
        <a href="/redirect/{{hash_id}}"
            title="{{extended}}">
            {{#if description}}
                {{description}}
            {{else}}
                [no title]
            {{/if}}
        </a>
    </div>

    <div class="actions">
        <span aria-hidden="true" class="icon" title="{{prettystored}}" data-icon="\"></span>
        <em class="icon">Date Stored</em>

        <a href="/bmark/readable/{{hash_id}}"
           title="View readable content"
           alt="View readable content"
           class="readable">
           <span aria-hidden="true" class="icon" data-icon="E"></span>
           <em class="icon">View readable content</em>
        </a> 

        {{#if owner}}
            <a href="/{{username}}/edit/{{hash_id}}"
                title="Edit the bookmark" alt="Edit the bookmark"
                class="edit">
                <span aria-hidden="true" class="icon" data-icon="p"></span>
                <em class="icon">Edit bookmark</em>
            </a>

            <a href="#" title="Delete the bookmark" alt="Delete the bookmark"
               class="delete">
                <span aria-hidden="true" class="icon" data-icon="*"></span>
                <em class="icon">Delete bookmark</em>
            </a>
       {{/if}}
    </div>
    {{#unless owner}}
        <div class="user">
            <a href="/{{username}}/recent" title="View {{username}}'s bookmarks">{{username}}</a>
        </div>
    {{/unless}}
    <div class="url" title="{{url}}">
        <a href="/bmark/readable/{{hash_id}}"
           title="View readable content" alt="View readable content">
           <span aria-hidden="true" class="icon" data-icon="E"></span>
           <em class="icon">View readable content</em>
        </a> {{url}}
    </div>
</script>


<script type="text/template" id="previous_control">
    {{#if show_previous}}
        <a href="#" class="button previous"><span aria-hidden="true" class="icon" data-icon="["></span> Prev</a>
    {{/if}}
</script>

<script type="text/template" id="next_control">
    {{#if show_next}}
        <a href="#" class="button next">Next <span class="icon"
        aria-hidden="true" data-icon="]"></span></a>
    {{/if}}
</script>

<script type="text/template" id="bmark_list">
    <div class="controls">
        <div class="" style="float: right;">
            <div class="buttons paging" style="display: inline-block;"></div>
        </div>

        {{#if current_user}}
            <div class="buttons add" style="display: inline-block; vertical-align: middle;">
                <a href="/{{current_user}}/new"
                    class="button">
                    <span class="icon" data-icon="&" aria-hidden="true"></span> Add Bookmark
                </a>
            </div>
        {{/if}}

        <div class="filter_control">
            {{{filter_control}}}
        </div>
    </div>

    <div class="data_list"></div>

    <div class="controls">
        <div class="" style="float: right;">
            <div class="buttons paging" style="display: inline-block;"></div>
        </div>
    </div>
</script>


<script type="text/template" id="filter_container">
    <div class="tag_filter_container" style="">
        <input name="tag_filter" id="tag_filter" value=""/>
    </div>
</script>


<script type="text/template" id="bmark_search">
    <form id="bmark_search" name="bmark_search">
            <input type="text" id="search_phrase" value="{{phrase}}"/>
            <input type="checkbox"
                {{#if with_content}}checked="checked"{{/if}}
                name="with_content"
                id="with_content"
                />
                <label for="with_content">Content</label>
            <input type="submit"/>
    </form>
</script>
