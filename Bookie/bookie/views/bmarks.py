"""Controllers related to viewing lists of bookmarks"""
from bookie.models import BmarkMgr


RESULTS_MAX = 50


def list(request):
    """Display a list of bookmarks"""
    pass


def recent(request):
    """Most recent list of bookmarks capped at MAX"""
    rdict = request.matchdict

    # check if we have a page count submitted
    page = int(rdict.get('page', '0'))

    recent_list = BmarkMgr.recent(limit=RESULTS_MAX,
                           with_tags=True,
                           page=page)

    return { 'bmarks': recent_list,
             'count': RESULTS_MAX,
             'page': page,
             'route_url': request.route_url,
           }
