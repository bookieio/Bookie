"""Controllers related to viewing lists of bookmarks"""
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from bookie.lib.access import ReqAuthorize
from bookie.lib.urlhash import generate_hash
from bookie.lib.utils import parse_bool
from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import TagMgr

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


@view_config(
    route_name="bmark_recent",
    renderer="/bmark/recent.mako")
@view_config(
    route_name="bmark_recent_tags",
    renderer="/bmark/recent.mako")
@view_config(
    route_name="user_bmark_recent",
    renderer="/bmark/recent.mako")
@view_config(
    route_name="user_bmark_recent_tags",
    renderer="/bmark/recent.mako")
def recent(request):
    """Testing a JS driven ui with backbone/etc"""
    rdict = request.matchdict
    params = request.params

    # check for auth related stuff
    # are we looking for a specific user
    username = rdict.get('username', None)

    # do we have any tags to filter upon
    tags = rdict.get('tags', None)

    if isinstance(tags, str):
        tags = [tags]

    ret = {
        'username': username,
        'tags': tags,
    }

    # if we've got url parameters for the page/count then use those to help
    # feed the init of the ajax script
    ret['count'] = params.get('count') if 'count' in params else RESULTS_MAX
    ret['page'] = params.get('page') if 'page' in params else 0

    if parse_bool(request.registry.settings.get('single_user_mode', False)):
        ret['all_bookmark_title'] = 'Bookmark'
    else:
        ret['all_bookmark_title'] = 'All'

    return ret


@view_config(
    route_name="user_bmark_edit",
    renderer="/bmark/edit.mako")
@view_config(
    route_name="user_bmark_new",
    renderer="/bmark/edit.mako")
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
                    location = request.route_url(
                        'user_bmark_edit',
                        hash_id=new_url_hash,
                        username=request.user.username
                    )
                    return HTTPFound(location)

            new = True
            desc = params.get('description', None)
            bmark = Bmark(url, request.user.username, desc=desc)

        tag_suggest = TagMgr.suggestions(
            url=bmark.hashed.url,
            username=request.user.username
        )

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


@view_config(
    route_name="bmark_readable",
    renderer="/bmark/readable.mako")
def readable(request):
    """Display a readable version of this url if we can"""
    rdict = request.matchdict
    bid = rdict.get('hash_id', None)
    username = rdict.get('username', None)

    if bid:
        found = BmarkMgr.get_by_hash(bid, username=username)
        if found:
            return {
                'bmark': found,
                'username': username,
            }
        else:
            return HTTPNotFound()
