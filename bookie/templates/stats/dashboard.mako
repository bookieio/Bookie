<%inherit file="/main_wrap.mako" />
<%def name="title()">Bookie Dashboard</%def>

<h2>User Data</h2>

<ul>
    <li><span class="label">Users:</span> ${user_data['count']}</li>
    <li><span class="label">Pending Activations:</span> ${user_data['activations']}</li>
    <li><span class="label">Users with Bookmarks:</span> ${user_data['with_bookmarks']}</li>
</ul>


<h2>Bookmark Data</h2>

<ul>
    <li>
        <span class="label">Bookmarks:</span>
        ${bookmark_data['count']}
    </li>
    <li>
        <span class="label">Unique Urls:</span>
        ${bookmark_data['unique_count']}
    </li>
</ul>
