"""Controllers related to viewing lists of bookmarks"""
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from bookie.lib.access import ReqAuthorize
from bookie.lib.urlhash import generate_hash
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import Hashed
from bookie.models import TagMgr

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


@view_config(route_name="bmark_recent", renderer="/bmark/recent.mako")
@view_config(route_name="bmark_recent_tags", renderer="/bmark/recent.mako")
@view_config(route_name="user_bmark_recent", renderer="/bmark/recent.mako")
@view_config(route_name="user_bmark_recent_tags",
             renderer="/bmark/recent.mako")
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
@view_config(route_name="user_bmark_popular_tags",
             renderer="/bmark/popular.mako")
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


@view_config(route_name="user_bmark_edit", renderer="/bmark/edit.mako")
@view_config(route_name="user_bmark_new", renderer="/bmark/edit.mako")
def edit(request):
    """Manual add a bookmark to the user account

    Can pass in params (say from a magic bookmarklet later)
    url
    description
    extended
    tags

    """
    rdict = request.matchdict
    params = request.params
    new = False

    with ReqAuthorize(request, username=rdict['username']):

        if 'hash_id' in rdict:
            hash_id = rdict['hash_id']
        elif 'hash_id' in params:
            hash_id = params['hash_id']
        else:
            hash_id = None

        if hash_id:
            bmark = BmarkMgr.get_by_hash(hash_id, request.user.username)

            if bmark is None:
                return HTTPNotFound()
        else:
            # hash the url and make sure that it doesn't exist
            url = params.get('url', "")
            if url != "":
                new_url_hash = generate_hash(url)

                test_exists = BmarkMgr.get_by_hash(new_url_hash,
                                                   request.user.username)

                if test_exists:
                    location=request.route_url('user_bmark_edit',
                                               hash_id=new_url_hash,
                                               username=request.user.username)
                    return HTTPFound(location)

            new = True
            desc = params.get('description', None)
            bmark = Bmark(url, request.user.username, desc=desc)

        tag_suggest = TagMgr.suggestions(url=bmark.hashed.url)

        return {
                'new': new,
                'bmark': bmark,
                'user': request.user,
                'tag_suggest': tag_suggest,
        }


@view_config(route_name="user_bmark_edit_error", renderer="/bmark/edit.mako")
@view_config(route_name="user_bmark_new_error", renderer="/bmark/edit.mako")
def edit_error(request):
    rdict = request.matchdict
    params = request.params
    post = request.POST

    with ReqAuthorize(request, username=rdict['username']):
        if 'new' in request.url:
            BmarkMgr.store(post['url'],
                           request.user.username,
                           post['description'],
                           post['extended'],
                           post['tags'])

        else:
            if 'hash_id' in rdict:
                hash_id = rdict['hash_id']
            elif 'hash_id' in params:
                hash_id = params['hash_id']

            bmark = BmarkMgr.get_by_hash(hash_id, request.user.username)
            if bmark is None:
                return HTTPNotFound()

            bmark.fromdict(post)
            bmark.update_tags(post['tags'])

        # if this is a new bookmark from a url, offer to go back to that url
        # for the user. 
        if 'go_back' in params and params['comes_from'] != "":
            return HTTPFound(location=params['comes_from'])
        else:
            return HTTPFound(
                location=request.route_url('user_bmark_recent',
                                           username=request.user.username))


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
