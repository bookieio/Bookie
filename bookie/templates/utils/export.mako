<!DOCTYPE NETSCAPE-Bookmark-file-1>
<% import time %>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<!-- This is an automatically generated file.
  It will be read and overwritten.
  Do Not Edit! -->
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    % for bmark in bmark_list:
        <DT>
            <A HREF="${bmark.hashed.url}" LAST_VISIT="" ADD_DATE="${time.mktime(bmark.stored.timetuple())}"
               TAGS="${','.join([tag for tag in bmark.tags])}">
                     % if bmark.description:
                         ${bmark.description}
                     % else:
                         ${bmark.hashed.url}
                     % endif
            </A>
        % if bmark.extended != "" or bmark.extended is not None:
        <DD>${bmark.extended}
        % endif
    % endfor
</DL><p>