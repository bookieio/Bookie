"""Basic views with no home"""
import logging
from pyramid.view import view_config

from bookie.lib.access import ReqAuthorize
from bookie.models.auth import UserMgr


LOG = logging.getLogger(__name__)


@view_config(route_name="dashboard",
             renderer="/stats/dashboard.mako")
def dashboard(self):
    """A public dashboard of the system"""
    return {}


@view_config(route_name="user_stats", renderer="/stats/userstats.mako")
def userstats(request):
    """Stats for an individual user"""
    with ReqAuthorize(request):
        user = UserMgr.get(username=request.user.username)
    return {
        'user': user,
        'username': user.username,
    }
