<%inherit file="/main_wrap.mako" />
<%def name="title()">Bookie Dashboard</%def>

<h2>Number of items in the system</h2>
<img src="/static/rrd/systemcount.png" alt="Import queue depth"></img>

<h2>Average import queue depth</h2>
<img src="/static/rrd/import_queue_depth.png" alt="Import queue depth"></img>
