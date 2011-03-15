<%inherit file="/main_wrap.mako" />
<%namespace file="../bmark/func.mako" import="display_bmark_list, bmarknextprev"/>
<%def name="title()">Import Bookmarks</%def>

<h1>Import Delicious export file</h1>

% if error:
    <h3>
    % for err in error:
        ${err}
    % endfor
    </h3>
% endif
