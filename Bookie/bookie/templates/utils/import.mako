<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev"/>
<%def name="title()">Import Bookmarks</%def>

<h1>Import Bookmarks</h1>

<div class="yui3-g">
    <div class="yui3-u-3-4">

    % if error:
        <h3>
        % for err in error:
            ${err}
        % endfor
        </h3>
    % endif

        <div class="block">
            <div class="head"></div>
            <div class="body">
                <form class="" action="${request.route_url('utils_import')}" method="POST" enctype=multipart/form-data>
                    <fieldset>
                        <ul>
                            <li>
                                <label for="import_file">Import File</label>
                                <input type="file" name="import_file" id="import_file" />
                            </li>
                            <li>
                                <label for="api_key">Api Key</label>
                                <input type="password" name="api_key" id="api_key" />
                            </li>

                            <li>
                                <input type="submit" name="upload" value="Upload" id="upload" />
                            </li>
                        </ul>
                    </fieldset>
                </form>
            </div>
            <div class="head"></div>
        </div>
    </div>
    <div class="yui3-u-1-4">
        <div class="note">
            <p>Use the <em>Import Bookmarks</em> tool to import your bookmarks from Delicious 
            or Google Bookmarks.</p>
            <p>You will need an html export file from either of these services.</p>
            <h2>Delicious</h2>
            <p>To get an html file from Delicious, click on <em>Settings</em> and then click on 
            the <em>Export / Backup Bookmarks</em> link under the <em>Bookmarks</em> heading.</p>
            <h2>Google Bookmarks</h2>
            <p>To get an html file from Google Bookmarks, click on <em>Export Bookmarks</em>
            under the <em>Tools</em> heading on the sidebar.</p>

            <p>Note that the import process might take a bit of time on large sets of bookmarks.</p>
        </div>
    </div>
</div>
