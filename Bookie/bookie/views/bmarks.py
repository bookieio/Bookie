"""Controllers related to viewing lists of bookmarks"""
import logging

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

from bookie.lib.access import edit_enabled
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import BmarkMgr

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


def recent(request):
    """Most recent list of bookmarks capped at MAX"""
    rdict = request.matchdict

    # check if we have a page count submitted
    page = int(rdict.get('page', '0'))

    recent_list = BmarkMgr.recent(limit=RESULTS_MAX,
                           with_tags=True,
                           page=page)

    return {
             'bmarks': recent_list,
             'max_count': RESULTS_MAX,
             'count': len(recent_list),
             'page': page,
             'allow_edit': edit_enabled(request.registry.settings),
           }


def confirmdelete(request):
    """Confirm deletion of bookmark"""
    rdict = request.matchdict
    bid = int(rdict.get('bid'))
    return {
            'bid': bid,
           }


def delete(request):
    """Remove the bookmark in question"""
    rdict = request.matchdict

    if not edit_enabled(request.registry.settings):
        raise HTTPForbidden("Auth to edit is not enabled")

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
