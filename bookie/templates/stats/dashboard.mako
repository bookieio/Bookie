<%inherit file="/main_wrap.mako" />
<%def name="title()">Bookie Dashboard</%def>

<h2>User Data</h2>

<ul>
    <li><span class="label">Users:</span> ${user_data['count']}</li>
    <li><span class="label">Pending Activations:</span> ${user_data['activations']}</li>

</ul>


<h2>Bookmark Data</h2>

<ul>
    <li><span class="label">Bookmarks:</span> ${bookmark_data['count']}</li>

</ul>

<h2>Number of items in the system</h2>
<img src="/static/rrd/systemcount.png" alt="Import queue depth"></img>

<h2>Average import queue depth</h2>
<img src="/static/rrd/import_queue_depth.png" alt="Import queue depth"></img>
