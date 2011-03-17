<%inherit file="/main_wrap.mako" />
<%def name="title()">Delete bookmark?</%def>

<h2>Really Delete?</h2>

<a href="${request.route_url('bmark_delete', bid=bid)}">Yes</a>      <a href="/">No</a>

