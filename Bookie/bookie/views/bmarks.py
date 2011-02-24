from bookie.models import DBSession, NoResultFound
from bookie.models import Bmark, BmarkMgr
from pyramid.httpexceptions import HTTPNotFound


RESULTS_MAX = 50

def list(request):
    """Display a list of bookmarks"""
    pass


def recent(request):
    """Most recent list of bookmarks capped at MAX"""
    recent = BmarkMgr.find(order_by=Bmark.stored.desc(),
                           limit=RESULTS_MAX,
                           with_tags=True, )

    return { 'bmarks': recent,
             'count': RESULTS_MAX,
           }
