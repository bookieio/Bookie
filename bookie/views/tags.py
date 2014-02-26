"""Controllers related to viewing Tag information"""
import logging
from pyramid.view import view_config

from bookie.models import TagMgr
from bookie.views import bmarks

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


@view_config(route_name="tag_list", renderer="/tag/list.mako")
@view_config(route_name="user_tag_list", renderer="/tag/list.mako")
def tag_list(request):
    """Display a list of your tags"""
    rdict = request.matchdict
    username = rdict.get("username", None)
    if username:
        username = username.lower()

    tags_found = TagMgr.find(username=username)

    return {
        'tag_list': tags_found,
        'tag_count': len(tags_found),
        'username': username,
    }


@view_config(route_name="tag_bmarks", renderer="/bmark/recent.mako")
@view_config(route_name="user_tag_bmarks", renderer="/bmark/recent.mako")
def bmark_list(request):
    """Display the list of bookmarks for this tag"""
    # Removed because view was deprecated
    return bmarks.recent(request)
