"""Controllers related to viewing lists of bookmarks"""
import logging

from datetime import datetime
from pyramid.settings import asbool
from pyramid.view import view_config
from StringIO import StringIO

from bookie.lib.access import ApiAuthorize
from bookie.lib.readable import ReadContent
from bookie.lib.tagcommands import Commander

from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import DBSession
from bookie.models import Hashed
from bookie.models import NoResultFound
from bookie.models import Readable
from bookie.models import TagMgr
from bookie.models.auth import UserMgr

from bookie.models.fulltext import get_fulltext_handler

LOG = logging.getLogger(__name__)
RESULTS_MAX = 10
HARD_MAX = 100


@view_config(route_name="api_bmark_recent", renderer="morjson")
@view_config(route_name="user_api_bmark_recent", renderer="morjson")
def bmark_recent(request):
    """Get a list of the bmarks for the api call"""
    rdict = request.matchdict
    params = request.params

    # check if we have a page count submitted
    page = int(params.get('page', '0'))
    count = int(params.get('count', RESULTS_MAX))
    username = rdict.get('username', None)

    # thou shalt not have more then the HARD MAX
    # @todo move this to the .ini as a setting
    if count > HARD_MAX:
        count = HARD_MAX

    # do we have any tags to filter upon
    tags = rdict.get('tags', None)

    if isinstance(tags, str):
        tags = [tags]

    # if we don't have tags, we might have them sent by a non-js browser as a
    # string in a query string
    if not tags and 'tag_filter' in params:
        tags = params.get('tag_filter').split()

    recent_list = BmarkMgr.find(limit=count,
                           order_by=Bmark.stored.desc(),
                           tags=tags,
                           page=page,
                           with_tags=True,
                           username=username)

    result_set = []

    for res in recent_list:
        return_obj = dict(res)
        return_obj['tags'] = [dict(tag[1]) for tag in res.tags.items()]
        result_set.append(return_obj)

    ret = {
        'success': True,
        'message': "",
        'payload': {
             'bmarks': result_set,
             'max_count': RESULTS_MAX,
             'count': len(recent_list),
             'page': page,
             'tags': tags,
        }

    }

    return ret


@view_config(route_name="api_bmark_popular", renderer="morjson")
@view_config(route_name="user_api_bmark_popular", renderer="morjson")
def bmark_popular(request):
    """Get a list of the bmarks for the api call"""
    rdict = request.matchdict
    params = request.params

    # check if we have a page count submitted
    page = int(params.get('page', '0'))
    count = int(params.get('count', RESULTS_MAX))
    username = rdict.get('username', None)

    # thou shalt not have more then the HARD MAX
    # @todo move this to the .ini as a setting
    if count > HARD_MAX:
        count = HARD_MAX

    # do we have any tags to filter upon
    tags = rdict.get('tags', None)

    if isinstance(tags, str):
        tags = [tags]

    # if we don't have tags, we might have them sent by a non-js browser as a
    # string in a query string
    if not tags and 'tag_filter' in params:
        tags = params.get('tag_filter').split()

    popular_list = BmarkMgr.find(limit=count,
                           order_by=Bmark.clicks.desc(),
                           tags=tags,
                           page=page,
                           username=username)
    result_set = []

    for res in popular_list:
        return_obj = dict(res)
        return_obj['tags'] = [dict(tag[1]) for tag in res.tags.items()]
        result_set.append(return_obj)

    ret = {
        'success': True,
        'message': "",
        'payload': {
             'bmarks': result_set,
             'max_count': RESULTS_MAX,
             'count': len(popular_list),
             'page': page,
             'tags': tags,
        }

    }

    return ret


@view_config(route_name="user_api_bmark_sync", renderer="morjson")
def bmark_sync(request):
    """Return a list of the bookmarks we know of in the system

    For right now, send down a list of hash_ids

    """
    rdict = request.matchdict
    params = request.params

    username = rdict.get('username', None)
    user = UserMgr.get(username=username)

    with ApiAuthorize(user.api_key,
                      params.get('api_key', None)):

        hash_list = BmarkMgr.hash_list(username=username)

        ret = {
            'success': True,
            'message': "",
            'payload': {
                 'hash_list': [hash[0] for hash in hash_list]
            }
        }

        return ret


@view_config(route_name="api_bmark_hash", renderer="morjson")
@view_config(route_name="user_api_bmark_hash", renderer="morjson")
def bmark_get(request):
    """Return a bookmark requested via hash_id

    We need to return a nested object with parts
        bmark
            - readable
    """
    rdict = request.matchdict
    params = request.params

    hash_id = rdict.get('hash_id', None)
    username = rdict.get('username', None)

    if not hash_id:
        return {
            'success': False,
            'message': "Could not find bookmark for hash " + hash_id,
            'payload': {}
        }

    bookmark = BmarkMgr.get_by_hash(hash_id,
                                    username=username)

    LOG.debug("BOOKMARK FOUND")
    LOG.debug(bookmark)
    if bookmark is None:
        # then not found
        # check to see if they want the last tags used on the last bookmark
        # but only for the last
        if 'last_bmark' in request.params:
            last = BmarkMgr.get_recent_bmark(username=username)
            if last is not None:
                payload = {'last':  dict(last)}
            else:
                payload = {}
        else:
            payload = {}

        ret = {
            'success': False,
            'message': "Bookmark for hash id {0} not found".format(hash_id),
            'payload': payload
        }

    else:
        return_obj = dict(bookmark)
        if bookmark.hashed.readable:
            return_obj['readable'] = dict(bookmark.hashed.readable)

        return_obj['tags'] = [dict(tag[1]) for tag in bookmark.tags.items()]

        ret = {
            'success': True,
            'message': "",
            'payload': {
                 'bmark': return_obj
            }
        }

    return ret


@view_config(route_name="user_api_bmark_add", renderer="morjson")
def bmark_add(request):
    """Add a new bookmark to the system"""
    params = request.params
    rdict = request.matchdict

    username = rdict.get("username", None)
    user = UserMgr.get(username=username)

    with ApiAuthorize(user.api_key,
                      params.get('api_key', None)):

        if 'url' in params and params['url']:
            # check if we already have this
            try:
                mark = BmarkMgr.get_by_url(params['url'],
                                           username=username)

                mark.description = params.get('description', mark.description)
                mark.extended = params.get('extended', mark.extended)

                new_tag_str = params.get('tags', None)

                # if the only new tags are commands, then don't erase the
                # existing tags
                # we need to process any commands associated as well
                new_tags = TagMgr.from_string(new_tag_str)
                found_cmds = Commander.check_commands(new_tags)

                if new_tag_str and len(new_tags) == len(found_cmds):
                    # the all the new tags are command tags, just tack them on
                    # for processing, but don't touch existing tags
                    for command_tag in new_tags.values():
                        LOG.debug(command_tag)
                        mark.tags[command_tag.name] = command_tag
                else:
                    if new_tag_str:
                        # in this case, rewrite the tags wit the new ones
                        mark.update_tags(new_tag_str)

                commander = Commander(mark)
                mark = commander.process()

            except NoResultFound:
                # then let's store this thing
                # if we have a dt param then set the date to be that manual
                # date
                if 'dt' in request.params:
                    # date format by delapi specs:
                    # CCYY-MM-DDThh:mm:ssZ
                    fmt = "%Y-%m-%dT%H:%M:%SZ"
                    stored_time = datetime.strptime(request.params['dt'], fmt)
                else:
                    stored_time = None

                # we want to store fulltext info so send that along to the
                # import processor
                conn_str = request.registry.settings.get('sqlalchemy.url',
                                                         False)
                fulltext = get_fulltext_handler(conn_str)

                LOG.debug('Username')
                LOG.debug(username)
                mark = BmarkMgr.store(params['url'],
                             username,
                             params.get('description', ''),
                             params.get('extended', ''),
                             params.get('tags', ''),
                             dt=stored_time,
                             fulltext=fulltext,
                       )

                # we need to process any commands associated as well
                commander = Commander(mark)
                mark = commander.process()

            # if we have content, stick it on the object here
            if 'content' in request.params:
                content = StringIO(request.params['content'])
                content.seek(0)
                parsed = ReadContent.parse(content, content_type="text/html")

                mark.hashed.readable = Readable()
                mark.hashed.readable.content = parsed.content
                mark.hashed.readable.content_type = parsed.content_type
                mark.hashed.readable.status_code = parsed.status
                mark.hashed.readable.status_message = parsed.status_message

            # we need to flush here for new tag ids, etc
            DBSession.flush()

            mark_data = dict(mark)
            mark_data['tags'] = [dict(mark.tags[tag]) for tag in mark.tags.keys()]

            return {
                        'success': True,
                        'message': "done",
                        'payload': {
                            'bmark': mark_data
                        }
                    }
        else:
            return {'success': False,
                    'message': 'Bad Request: missing url',
                    'payload': dict(params)
                 }


@view_config(route_name="user_api_bmark_remove", renderer="morjson")
def bmark_remove(request):
    """Remove this bookmark from the system"""
    params = request.params
    rdict = request.matchdict

    username = rdict.get("username", None)
    user = UserMgr.get(username=username)

    with ApiAuthorize(user.api_key,
                      params.get('api_key', None)):

        if 'url' in params and params['url']:
            try:
                bmark = BmarkMgr.get_by_url(params['url'],
                                            username=username)

                session = DBSession()
                session.delete(bmark)

                return {
                        'success': True,
                        'message': "done",
                        'payload': {}
                }

            except NoResultFound:
                # if it's not found, then there's not a bookmark to delete
                return {
                    'success': False,
                    'message': "Bad Request: bookmark not found",
                    'payload': {}

                }


@view_config(route_name="api_tag_complete", renderer="morjson")
@view_config(route_name="user_api_tag_complete", renderer="morjson")
def tag_complete(request):
    """Complete a tag based on the given text

    :@param tag: GET string, tag=sqlalchemy
    :@param current: GET string of tags we already have python+database

    """
    params = request.GET

    if 'current' in params and params['current'] != "":
        current_tags = params['current'].split()
    else:
        current_tags = None

    if 'tag' in params and params['tag']:
        tag = params['tag']
        tags = TagMgr.complete(tag, current=current_tags)
        # reset this for the payload join operation
        current_tags = []

    ret = {
        'success': True,
        'message': "",
        'payload': {
             'current': ",".join(current_tags),
             'tags': [tag.name for tag in tags]
        }
    }

    return ret


@view_config(route_name="api_bmark_get_readable", renderer="morjson")
def to_readable(request):
    """Get a list of urls, hash_ids we need to readable parse"""
    url_list = Hashed.query.outerjoin(Readable).\
                filter(Readable.imported == None).all()

    ret = {
        'success': True,
        'message': "",
        'payload': {
            'urls': [dict(h) for h in url_list]
        }
    }

    return ret

@view_config(route_name="api_bmark_readable", renderer="morjson")
def readable(request):
    """Take the html given and parse the content in there for readable

    :@param hash_id: POST the hash_id of the bookmark we're readable'ing
    :@param content: POST the html of the page in question

    """
    params = request.POST
    success = params.get('success', None)

    if success is None:
        ret = {
            'success': False,
            'message': "Please submit success data",
            'payload': {}
        }

    hashed = Hashed.query.get(params.get('hash_id', None))

    if hashed:
        success = asbool(success)
        LOG.debug(success)
        if success:
            # if we have content, stick it on the object here
            if 'content' in params:
                content = StringIO(params['content'])
                content.seek(0)
                parsed = ReadContent.parse(content, content_type="text/html")

                hashed.readable = Readable()
                hashed.readable.content = parsed.content
                hashed.readable.content_type = parsed.content_type
                hashed.readable.status_code = 200
                hashed.readable.status_message = "API Parsed"

                ret = {
                    'success': True,
                    'message': "Parsed url: " + hashed.url,
                    'payload': {}
                }
            else:
                ret = {
                    'success': False,
                    'message': "Missing content for hash id",
                    'payload': {
                        'hash_id': params.get('hash_id')
                    }
                }

        else:
            # success was false for some reason
            # could be an image, 404, error, bad domain...
            # need info for content_type, status_code, status_message
            hashed.readable = Readable()
            hashed.readable.content_type = params.get('content_type', "Unknown")
            hashed.readable.status_code = params.get('status_code', 999)
            hashed.readable.status_message = params.get('status_message', "Missing message")

            ret = {
                'success': True,
                'message': "Stored unsuccessful content fetching result",
                'payload': dict(params)
            }

    else:
        ret = {
            'success': False,
            'message': "Missing hash_id to parse",
            'payload': {}
        }

    return ret
