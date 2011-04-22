"""Controllers related to viewing lists of bookmarks"""
import logging

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

from bookie.lib import access
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import Hashed

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
             'allow_edit': access.edit_enabled(request.registry.settings),
           }


def popular(request):
    """Most popular list of bookmarks capped at MAX"""
    rdict = request.matchdict

    # check if we have a page count submitted
    page = int(rdict.get('page', '0'))

    popular_list = BmarkMgr.popular(limit=RESULTS_MAX,
                           with_tags=True,
                           page=page)


    return {
             'bmarks': popular_list,
             'max_count': RESULTS_MAX,
             'count': len(popular_list),
             'page': page,
             'allow_edit': access.edit_enabled(request.registry.settings),
           }


def confirm_delete(request):
    """Confirm deletion of bookmark"""
    rdict = request.matchdict
    bid = int(rdict.get('bid', 0))
    if bid:
        found = Bmark.query.get(bid)

    if not found:
        return HTTPNotFound()

    return {
            'bid': bid,
            'bmark_description': found.description
           }


def delete(request):
    """Remove the bookmark in question"""
    rdict = request.POST

    if not access.edit_enabled(request.registry.settings):
        raise HTTPForbidden("Auth to edit is not enabled")

    # make sure we have an id value
    bid = int(rdict.get('bid', 0))

    if bid:
        found = Bmark.query.get(bid)

        if found:
            DBSession.delete(found)
            return HTTPFound(location=request.route_url('bmark_recent'))

    return HTTPNotFound()

def readable(request):
    """Display a readable version of this url if we can"""
    rdict = request.matchdict
    bid = rdict.get('hash_id', None)

    if bid:
        found = Hashed.query.get(bid)
        return { 'bmark': found }
