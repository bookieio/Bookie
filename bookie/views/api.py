"""Controllers related to viewing lists of bookmarks"""
import logging

from datetime import datetime
from pyramid.settings import asbool
from pyramid.view import view_config
from StringIO import StringIO

from bookie.lib.access import api_auth
from bookie.lib.access import ApiAuthorize
from bookie.lib.access import ReqOrApiAuthorize
from bookie.lib.applog import AuthLog
from bookie.lib.applog import BmarkLog
from bookie.lib.message import ReactivateMsg
from bookie.lib.readable import ReadContent
from bookie.lib.tagcommands import Commander

from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import DBSession
from bookie.models import Hashed
from bookie.models import NoResultFound
from bookie.models import Readable
from bookie.models import TagMgr
from bookie.models.auth import ActivationMgr
from bookie.models.auth import UserMgr

from bookie.models.fulltext import get_fulltext_handler

LOG = logging.getLogger(__name__)
RESULTS_MAX = 10
HARD_MAX = 100

@view_config(route_name="api_bmark_hash", renderer="json")
@api_auth('api_key', UserMgr.get)
def bmark_get(request):
    """Return a bookmark requested via hash_id

    We need to return a nested object with parts
        bmark
            - readable
    """
    rdict = request.matchdict
    params = request.params

    hash_id = rdict.get('hash_id', None)
    username = request.user.username

    # the hash id will always be there or the route won't match
    bookmark = BmarkMgr.get_by_hash(hash_id,
                                    username=username)

    last_bmark = {}
    if 'last_bmark' in params and params['last_bmark'] != "false":
        last = BmarkMgr.get_recent_bmark(username=username)
        if last is not None:
            last_bmark = {'last':  dict(last)}

    if bookmark is None:
        request.response.status_int = 404
        ret = { 'error': "Bookmark for hash id {0} not found".format(hash_id) }
        ret.update(last_bmark)
        return ret
    else:
        return_obj = dict(bookmark)

        if 'with_content' in params and params['with_content'] != 'false':
            if bookmark.readable:
                return_obj['readable'] = dict(bookmark.readable)

        return_obj['tags'] = [dict(tag[1]) for tag in bookmark.tags.items()]

        ret = {'bmark': return_obj}
        ret.update(last_bmark)
        return ret

def _update_mark(mark, params):
    """Update the bookmark found with settings passed in"""
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
            mark.tags[command_tag.name] = command_tag
    else:
        if new_tag_str:
            # in this case, rewrite the tags wit the new ones
            mark.update_tags(new_tag_str)

    return mark


@view_config(route_name="api_bmark_add", renderer="json")
@view_config(route_name="api_bmark_update", renderer="json")
@api_auth('api_key', UserMgr.get)
def bmark_add(request):
    """Add a new bookmark to the system"""
    rdict = request.matchdict
    if 'url' in request.params or 'hash_id' in request.params:
        params = request.params
    elif 'url' in request.json_body or 'hash_id' in request.json_body:
        params = request.json_body
    else:
        request.response.status_int = 400
        return {
            'error': 'Bad Request: missing url',
         }

    user = request.user

    if 'url' not in params and 'hash_id' not in rdict:
        request.response.status_int = 400
        return {
            'error': 'Bad Request: missing url',
         }

    elif 'hash_id' in rdict:
        try:
            mark = BmarkMgr.get_by_hash(rdict['hash_id'],
                                       username=user.username)
            mark = _update_mark(mark, params)

        except NoResultFound:
            request.response.status_code = 404
            return {
                'error': 'Bookmark with hash id {0} not found.'.format(
                            rdict['hash_id'])
            }

    else:
        # check if we already have this
        try:
            mark = BmarkMgr.get_by_url(params['url'],
                                       username=user.username)
            mark = _update_mark(mark, params)

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

            # check to see if we know where this is coming from
            inserted_by = params.get('inserted_by', 'unknown_api')

            mark = BmarkMgr.store(params['url'],
                         user.username,
                         params.get('description', ''),
                         params.get('extended', ''),
                         params.get('tags', ''),
                         dt=stored_time,
                         inserted_by=inserted_by,
                   )

        # we need to process any commands associated as well
        commander = Commander(mark)
        mark = commander.process()

        # if we have content, stick it on the object here
        if 'content' in params:
            content = StringIO(params['content'])
            content.seek(0)
            parsed = ReadContent.parse(content, content_type="text/html")

            mark.readable = Readable()
            mark.readable.content = parsed.content
            mark.readable.content_type = parsed.content_type
            mark.readable.status_code = parsed.status
            mark.readable.status_message = parsed.status_message

        # we need to flush here for new tag ids, etc
        DBSession.flush()

        mark_data = dict(mark)
        mark_data['tags'] = [dict(mark.tags[tag]) for tag in mark.tags.keys()]

        return {
            'bmark': mark_data,
            'location': request.route_url('bmark_readable',
                                          hash_id=mark.hash_id,
                                          username=user.username),
        }


@view_config(route_name="api_bmark_remove", renderer="json")
@api_auth('api_key', UserMgr.get)
def bmark_remove(request):
    """Remove this bookmark from the system"""
    rdict = request.matchdict
    user = request.user

    try:
        bmark = BmarkMgr.get_by_hash(rdict['hash_id'],
                                    username=user.username)

        DBSession.delete(bmark)

        return {
            'message': "done",
        }

    except NoResultFound:
        request.response.status_code = 404
        return {
            'error': 'Bookmark with hash id {0} not found.'.format(
                        rdict['hash_id'])
        }


@view_config(route_name="api_bmarks", renderer="json")
@view_config(route_name="api_bmarks_user", renderer="json")
@view_config(route_name="api_bmarks_tags", renderer="json")
@view_config(route_name="api_bmarks_user_tags", renderer="json")
@api_auth('api_key', UserMgr.get, anon=True)
def bmark_recent(request):
    """Get a list of the bmarks for the api call"""
    LOG.debug('BMARK RECENT')
    rdict = request.matchdict
    params = request.params

    # check if we have a page count submitted
    page = int(params.get('page', '0'))
    count = int(params.get('count', RESULTS_MAX))
    with_content = True if 'with_content' in params and params['with_content'] != "false" else False

    # we only want to do the username if the username is in the url
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
                           page=page,
                           tags=tags,
                           username=username,
                           with_content=with_content,
                           with_tags=True,
                           )

    result_set = []

    for res in recent_list:
        return_obj = dict(res)
        return_obj['tags'] = [dict(tag[1]) for tag in res.tags.items()]

        # we should have the hashed information, we need the url and clicks as
        # total clicks to send back
        return_obj['url'] = res.hashed.url
        return_obj['total_clicks'] = res.hashed.clicks

        if with_content:
            return_obj['readable'] = dict(res.readable) if res.readable else {}

        result_set.append(return_obj)

    return {
         'bmarks': result_set,
         'max_count': RESULTS_MAX,
         'count': len(recent_list),
         'page': page,
         'tag_filter': tags,
    }


@view_config(route_name="api_bmarks_popular", renderer="json")
@view_config(route_name="api_bmarks_popular_user", renderer="json")
@api_auth('api_key', UserMgr.get, anon=True)
def bmark_popular(request):
    """Get a list of the most popular bmarks for the api call"""
    rdict = request.matchdict
    params = request.params

    # check if we have a page count submitted
    page = int(params.get('page', '0'))
    count = int(params.get('count', RESULTS_MAX))
    with_content = True if 'with_content' in params and params['with_content'] != "false" else False

    if request.user and request.user.username:
        username = request.user.username
    else:
        username = None

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
                           page=page,
                           tags=tags,
                           username=username,
                           with_content=with_content,
                           with_tags=True,
                           )

    result_set = []

    for res in popular_list:
        return_obj = dict(res)
        return_obj['tags'] = [dict(tag[1]) for tag in res.tags.items()]

        # the hashed object is there as well, we need to pull the url and
        # clicks from it as total_clicks
        return_obj['url'] = res.hashed.url
        return_obj['total_clicks'] = res.hashed.clicks

        if with_content:
            return_obj['readable'] = dict(res.hashed.readable)

        result_set.append(return_obj)

    return {
         'bmarks': result_set,
         'max_count': RESULTS_MAX,
         'count': len(popular_list),
         'page': page,
         'tag_filter': tags,
    }


@view_config(route_name="api_bmarks_export", renderer="json")
@api_auth('api_key', UserMgr.get)
def bmark_export(request):
    """Export via the api call to json dump

    """
    username = request.user.username

    bmark_list = BmarkMgr.user_dump(username)
    # log that the user exported this
    BmarkLog.export(username, username)

    def build_bmark(bmark):
        d = dict(bmark)
        d['hashed'] = dict(bmark.hashed)
        return d

    return {
        'bmarks': [build_bmark(bmark) for bmark in bmark_list],
        'count': len(bmark_list),
        'date': str(datetime.now())
    }


@view_config(route_name="api_extension_sync", renderer="json")
@api_auth('api_key', UserMgr.get)
def extension_sync(request):
    """Return a list of the bookmarks we know of in the system

    For right now, send down a list of hash_ids

    """
    username = request.user.username

    hash_list = BmarkMgr.hash_list(username=username)
    return {
            'hash_list': [hash[0] for hash in hash_list]
    }


@view_config(route_name="api_bmark_search", renderer="json")
@view_config(route_name="api_bmark_search_user", renderer="json")
@api_auth('api_key', UserMgr.get, anon=True)
def search_results(request):
    """Search for the query terms in the matchdict/GET params

    The ones in the matchdict win in the case that they both exist
    but we'll fall back to query string search=XXX

    with_content
        is always GET and specifies if we're searching the fulltext of pages

    """
    mdict = request.matchdict
    rdict = request.GET

    if 'terms' in mdict:
        phrase = " ".join(mdict['terms'])
    else:
        phrase = rdict.get('search', '')

    if request.user and request.user.username:
        username = request.user.username
    else:
        username = None

    # with content is always in the get string
    search_content = asbool(rdict.get('search_content', False))

    conn_str = request.registry.settings.get('sqlalchemy.url', False)
    searcher = get_fulltext_handler(conn_str)

    # check if we have a page count submitted
    page = rdict.get('page', 0)
    count = rdict.get('count', 10)

    if 'username' in mdict:
        with_user = True
    else:
        with_user = False

    res_list = searcher.search(phrase,
                               content=search_content,
                               username=username if with_user else None,
                               ct=count,
                               page=page)

    constructed_results = []
    for res in res_list:
        return_obj = dict(res)
        return_obj['tags'] = [dict(tag[1]) for tag in res.tags.items()]

        # the hashed object is there as well, we need to pull the url and
        # clicks from it as total_clicks
        return_obj['url'] = res.hashed.url
        return_obj['total_clicks'] = res.hashed.clicks

        constructed_results.append(return_obj)

    return {
        'search_results': constructed_results,
        'result_count': len(constructed_results),
        'phrase': phrase,
        'page': page,
        'with_content': search_content,
        'username': username,
    }


@view_config(route_name="api_tag_complete", renderer="json")
@view_config(route_name="api_tag_complete_user", renderer="json")
@api_auth('api_key', UserMgr.get, anon=True)
def tag_complete(request):
    """Complete a tag based on the given text

    :@param tag: GET string, tag=sqlalchemy
    :@param current: GET string of tags we already have python+database

    """
    params = request.GET

    if request.user:
        username = request.user.username
    else:
        username = None

    if 'current' in params and params['current'] != "":
        current_tags = params['current'].split()
    else:
        current_tags = None

    if 'tag' in params and params['tag']:
        tag = params['tag']

        tags = TagMgr.complete(tag,
                               current=current_tags,
                               username=username)
    else:
        tags = []

    # reset this for the payload join operation
    if current_tags is None:
        current_tags = []

    return {
        'current': ",".join(current_tags),
        'tags': [tag.name for tag in tags]
    }


# USER ACCOUNT INFORMATION CALLS
@view_config(route_name="api_user_account", renderer="json")
@api_auth('api_key', UserMgr.get)
def account_info(request):
    """Return the details of the user account specifed

    expecting username in matchdict
    We only return a subset of data. We're not sharing keys such as api_key,
    password hash, etc.

    """
    user = request.user

    return user.safe_data()


@view_config(route_name="api_user_account_update", renderer="json")
@api_auth('api_key', UserMgr.get)
def account_update(request):
    """Update the account information for a user

    :params name:
    :params email:

    Callable by either a logged in user or the api key for mobile apps/etc

    """
    params = request.params
    json_body = request.json_body
    user_acct = request.user

    if 'name' in params and params['name'] is not None:
        name = params.get('name')
        user_acct.name = name

    if 'name' in json_body and json_body['name'] is not None:
        name = json_body.get('name')
        user_acct.name = name

    if 'email' in params and params['email'] is not None:
        email = params.get('email')
        user_acct.email = email

    if 'email' in json_body and json_body['email'] is not None:
        email = json_body.get('email')
        user_acct.email = email

    return user_acct.safe_data()


@view_config(route_name="api_user_api_key", renderer="json")
@api_auth('api_key', UserMgr.get)
def api_key(request):
    """Return the currently logged in user's api key

    This api call is available both on the website via a currently logged in
    user and via a valid api key passed into the request. In this way we should
    be able to add this to the mobile view with an ajax call as well as we do
    into the account information on the main site.

    """
    user_acct = request.user
    return {
        'api_key': user_acct.api_key,
        'username': user_acct.username
    }


@view_config(route_name="api_user_reset_password", renderer="json")
@api_auth('api_key', UserMgr.get)
def reset_password(request):
    """Change a user's password from the current string

    :params current_password:
    :params new_password:

    Callable by either a logged in user or the api key for mobile apps/etc

    """
    params = request.params

    # now also load the password info
    current = params.get('current_password', None)
    new = params.get('new_password', None)

    # if we don't have any password info, try a json_body in case it's a json
    #POST
    if current is None and new is None:
        params = request.json_body
        current = params.get('current_password', None)
        new = params.get('new_password', None)

    user_acct = request.user

    LOG.error("PASSWD")
    LOG.error(current)
    LOG.error(new)
    if not UserMgr.acceptable_password(new):
        request.response.status_int = 406
        return {
                'username': user_acct.username,
                'error': "Come on, let's try a real password this time"
               }

    # before we change the password, let's verify it
    if user_acct.validate_password(current):
        # we're good to change it
        user_acct.password = new
        return {
                'username': user_acct.username,
                'message': "Password changed",
               }
    else:
        request.response.status_int = 403
        return {
                'username': user_acct.username,
                'error': "Ooops, there was a typo somewhere. Please check your request"
               }



@view_config(route_name="api_user_suspend", renderer="json")
def suspend_acct(request):
    """Reset a user account to enable them to change their password"""
    params = request.params
    user = request.user

    # we need to get the user from the email
    email = params.get('email', None)

    if email is None and hasattr(request, 'json_body'):
        # try the json body
        email = request.json_body.get('email', None)

    if user is None and email is None:
        request.response.status_int = 406
        return {
            'error':  "Please submit an email address",
        }

    if user is None and email is not None:
        user = UserMgr.get(email=email)

    if user is None:
        request.response.status_int = 404
        return {
            'error':  "Please submit a valid address",
            'email': email
        }

    # check if we've already gotten an activation for this user
    if user.activation is not None:
        request.response.status_int = 406
        return {
            'error':  """You've already marked your account for reactivation.
Please check your email for the reactivation link. Make sure to
check your spam folder.""",
            'username': user.username,
        }

    # mark them for reactivation
    user.reactivate("FORGOTTEN")

    # log it
    AuthLog.reactivate(user.username)

    # and then send an email notification
    # @todo the email side of things
    settings = request.registry.settings
    msg = ReactivateMsg(user.email,
                        "Activate your Bookie account",
                        settings)

    msg.send(request.route_url('reset',
                         username=user.username,
                         reset_key=user.activation.code))

    return {
        'message':  """Your account has been marked for reactivation. Please
                    check your email for instructions to reset your
                    password""",
    }


@view_config(route_name="api_user_suspend_remove", renderer="json")
def account_activate(request):
    """Reset a user after being suspended

    :param username: required to know what user we're resetting
    :param activation: code needed to activate
    :param password: new password to use for the user

    """
    params = request.params

    username = params.get('username', None)
    activation = params.get('code', None)
    password = params.get('password', None)

    if username is None and activation is None and password is None:
        # then try to get the same fields out of a json body
        json_body = request.json_body
        username = json_body.get('username', None)
        activation = json_body.get('code', None)
        password = json_body.get('password', None)

    if not UserMgr.acceptable_password(password):
        request.response.status_int = 406
        return {
            'error': "Come on, pick a real password please",
        }

    res = ActivationMgr.activate_user(username, activation, password)

    if res:
        # success so respond nicely
        AuthLog.reactivate(username, success=True, code=activation)
        return {
            'message': "Account activated, please log in.",
            'username': username,
        }
    else:
        AuthLog.reactivate(username, success=False, code=activation)
        request.response.status_int = 500
        return {
            'error': "There was an issue attempting to activate this account.",
        }


@view_config(route_name="api_admin_readable_todo", renderer="json")
@api_auth('api_key', UserMgr.get, admin_only=True)
def to_readable(request):
    """Get a list of urls, hash_ids we need to readable parse"""
    url_list = Hashed.query.outerjoin(Readable).\
                filter(Readable.imported == None).all()

    ret = {
        'urls': [dict(h) for h in url_list]
    }

    return ret
