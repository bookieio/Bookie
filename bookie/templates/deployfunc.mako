<%def name="installspecific()">
<!-- Put any site specific items in here such as google analytics codes and
such -->
<%
    import os
    fname = 'installspecific.txt'
    if os.path.exists(fname):
        return open(fname).read()
%>
</%def>
