"""Basic views with no home"""
import logging
from pyramid.view import view_config

from bookie.lib.access import ReqAuthorize
from bookie.models import BmarkMgr
from bookie.models.auth import ActivationMgr
from bookie.models.auth import UserMgr
from bookie.views import BookieView


LOG = logging.getLogger(__name__)


class DashboardView(BookieView):

    @view_config(route_name="dashboard",
                 renderer="/stats/dashboard.mako")
    def dashboard(self):
        """A public dashboard of the system"""
        # Generate some user data and stats
        user_count = UserMgr.count()
        pending_activations = ActivationMgr.count()

        # Generate some bookmark data.
        bookmark_count = BmarkMgr.count()
        unique_url_count = BmarkMgr.count(distinct=True)
        users_with_bookmarks = BmarkMgr.count(distinct_users=True)

        return {
            'bookmark_data': {
                'count': bookmark_count,
                'unique_count': unique_url_count,
            },
            'user_data': {
                'count': user_count,
                'activations': pending_activations,
                'with_bookmarks': users_with_bookmarks,
            }
        }


@view_config(route_name="user_stats", renderer="/stats/userstats.mako")
def userstats(request):
    """Stats for an individual user"""
    with ReqAuthorize(request):
        user = UserMgr.get(username=request.user.username)
    return {
        'user': user,
        'username': user.username,
    }
