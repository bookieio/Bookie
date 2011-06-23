"""Controllers related to viewing lists of bookmarks"""
import logging

from pyramid import security
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from bookie.lib import access
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import Hashed

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


@view_config(route_name="bmark_recent", renderer="/bmark/recent.mako")
@view_config(route_name="bmark_recent_tags", renderer="/bmark/recent.mako")
@view_config(route_name="user_bmark_recent", renderer="/bmark/recent.mako")
@view_config(route_name="user_bmark_recent_tags", renderer="/bmark/recent.mako")
def recent(request):
    """Most recent list of bookmarks capped at MAX"""
    rdict = request.matchdict
    params = request.params

    LOG.debug('in recent!')
    # check if we have a page count submitted
    page = int(params.get('page', '0'))

    # do we have any tags to filter upon
    tags = rdict.get('tags', None)

    if isinstance(tags, str):
        tags = [tags]

    # check for auth related stuff
    # are we looking for a specific user
    username = rdict.get('username', None)

    # if we don't have tags, we might have them sent by a non-js browser as a
    # string in a query string
    if not tags and 'tag_filter' in params:
        tags = params.get('tag_filter').split()

    recent_list = BmarkMgr.find(limit=RESULTS_MAX,
                           order_by=Bmark.stored.desc(),
                           tags=tags,
                           page=page,
                           username=username)

    ret = {
             'bmarks': recent_list,
             'max_count': RESULTS_MAX,
             'count': len(recent_list),
             'page': page,
             'tags': tags,
             'username': username,
           }

    return ret


@view_config(route_name="bmark_popular", renderer="/bmark/popular.mako")
@view_config(route_name="user_bmark_popular", renderer="/bmark/popular.mako")
@view_config(route_name="bmark_popular_tags", renderer="/bmark/popular.mako")
@view_config(route_name="user_bmark_popular_tags", renderer="/bmark/popular.mako")
def popular(request):
    """Most popular list of bookmarks capped at MAX"""
    rdict = request.matchdict
    params = request.params

    # check if we have a page count submitted
    tags = rdict.get('tags', None)
    page = int(params.get('page', '0'))

    if isinstance(tags, str):
        tags = [tags]

    # check for auth related stuff
    # are we looking for a specific user
    username = rdict.get('username', None)

    # if we don't have tags, we might have them sent by a non-js browser as a
    # string in a query string
    if not tags and 'tag_filter' in params:
        tags = params.get('tag_filter').split()

    recent_list = BmarkMgr.find(limit=RESULTS_MAX,
                           order_by=Bmark.clicks.desc(),
                           tags=tags,
                           page=page,
                           username=username, )

    return {
             'bmarks': recent_list,
             'max_count': RESULTS_MAX,
             'count': len(recent_list),
             'page': page,
             'tags': tags,
             'user': request.user,
             'username': username,
           }


@view_config(route_name="bmark_delete")
def delete(request):
    """Remove the bookmark in question"""
    rdict = request.POST

    # make sure we have an id value
    bid = int(rdict.get('bid', 0))

    if bid:
        found = Bmark.query.get(bid)

        if found:
            DBSession.delete(found)
            return HTTPFound(location=request.route_url('bmark_recent'))

    return HTTPNotFound()


@view_config(route_name="bmark_confirm_delete",
             renderer="/bmark/confirm_delete.mako")
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


@view_config(route_name="bmark_readable", renderer="/bmark/readable.mako")
def readable(request):
    """Display a readable version of this url if we can"""
    rdict = request.matchdict
    bid = rdict.get('hash_id', None)
    username = rdict.get('username', None)

    if bid:
        found = Hashed.query.get(bid)
        if found:
            return {
                    'bmark': found,
                    'username': username,
                    }
        else:
            return HTTPNotFound()
