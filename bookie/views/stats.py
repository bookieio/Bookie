"""Basic views with no home"""
import logging
from pyramid.view import view_config

from bookie.bcelery import tasks
from bookie.models import BmarkMgr
from bookie.models.auth import ActivationMgr
from bookie.models.auth import UserMgr


LOG = logging.getLogger(__name__)


@view_config(
    route_name="dashboard",
    renderer="/stats/dashboard.mako")
def dashboard(request):
    """A public dashboard of the system
    """
    res = tasks.count_total.delay()

    # Generate some user data and stats
    user_count = UserMgr.count()
    pending_activations = ActivationMgr.count()

    # Generate some bookmark data.
    bookmark_count = BmarkMgr.count()
    unique_url_count = BmarkMgr.count(distinct=True)

    return {
        'bookmark_data': {
            'count': bookmark_count,
            'unique_count': unique_url_count
        },
        'user_data': {
            'count': user_count,
            'activations': pending_activations

        }
    }
