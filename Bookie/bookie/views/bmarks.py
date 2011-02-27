from bookie.models import DBSession
from bookie.models import NoResultFound
from bookie.models import Bmark
from bookie.models import BmarkMgr

from pyramid.httpexceptions import HTTPNotFound
from pyramid.url import route_url


RESULTS_MAX = 50

def list(request):
    """Display a list of bookmarks"""
    pass


def recent(request):
    """Most recent list of bookmarks capped at MAX"""
    rdict = request.matchdict

    # check if we have a page count submitted
    page = int(rdict.get('page', '0'))

    recent = BmarkMgr.recent(limit=RESULTS_MAX,
                           with_tags=True,
                           page=page)

    return { 'bmarks': recent,
             'count': RESULTS_MAX,
             'page': page,
             'route_url': request.route_url,
           }
