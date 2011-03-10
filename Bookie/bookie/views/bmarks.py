"""Controllers related to viewing lists of bookmarks"""
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.settings import asbool

from bookie.models import DBSession
from bookie.models import Bmark
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
             'allow_edit': asbool(request.registry.settings.get('allow_edit', 0)),
           }

def delete(request):
    """Remove the bookmark in question"""
    rdict = request.matchdict

    # make sure we have an id value
    bid = int(rdict.get('bid', 0))

    if bid:
        found = Bmark.query.get(bid)

        if found:
            DBSession.delete(found)

            return HTTPFound(location=request.route_url('bmark_recent'))
        else:
            return HTTPNotFound()
    else:
        return HTTPNotFound()
