<%inherit file="/main_wrap.mako" />
<%def name="title()">Delete bookmark?</%def>


<h2 style="text-align:center">Delete Confirmation</h2>
<form method="post" action="${request.route_url('user_bmark_delete')}" style="text-align:center">
    <p>Are you sure you want delete the following bookmark?</p>
    <p><em>${bmark_description}</em></p>
    <input type="hidden" id="bid" name="bid" value="${bid}" />
    <!-- ew, onclick. This page will be replaced by a nice ajaxy delete confirmation, so it's ok. -->
    <input id="cancel" type="button" value="Cancel" style="padding:2px;margin-right:40px" onclick="location.href='${app_url}'" />
    <input id="delete" type="submit" value="Delete" style="padding:2px;" />
</form>
