<%def name="installspecific()">
<!-- Put any site specific items in here such as google analytics codes and
such -->
<%
    import os
    fname = request.registry.settings['installspecific']
    if os.path.exists(fname):
        return open(fname).read()
%>
</%def>
