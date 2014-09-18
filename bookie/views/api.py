"""Controllers related to viewing lists of bookmarks"""
import logging

from datetime import datetime
from pyramid.settings import asbool
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import contains_eager
from StringIO import StringIO

from bookie.bcelery import tasks
from bookie.lib.access import api_auth
from bookie.lib.applog import AuthLog
from bookie.lib.applog import BmarkLog
from bookie.lib.message import ReactivateMsg
from bookie.lib.message import ActivationMsg
from bookie.lib.readable import ReadContent
from bookie.lib.tagcommands import Commander
from bookie.lib.utils import suggest_tags

from bookie.models import (
    bmarks_tags,
    Bmark,
    BmarkMgr,
    DBSession,
    Hashed,
    NoResultFound,
    Readable,
    TagMgr,
)
from bookie.models.applog import AppLogMgr
from bookie.models.auth import ActivationMgr
from bookie.models.auth import get_random_word
from bookie.models.auth import User
from bookie.models.auth import UserMgr
from bookie.models.stats import StatBookmarkMgr
from bookie.models.queue import ImportQueueMgr
from bookie.models.social import SocialMgr
from bookie.models.fulltext import get_fulltext_handler

LOG = logging.getLogger(__name__)
RESULTS_MAX = 10
HARD_MAX = 100


def _check_with_content(params):
    """Verify that we should be checking with content"""
    if 'with_content' in params and params['with_content'] != 'false':
        return True
    else:
        return False


def _api_response(request, data):
    """Perform common operations on the response."""
    # Wrap the data response with CORS headers for cross domain JS clients.
    request.response.headers.extend([
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Headers', 'X-Requested-With')
    ])

    return data


@view_config(route_name="api_user_stats", renderer="jsonp")
def user_stats(request):
    """Return all the user stats"""
    user_count = UserMgr.count()
    pending_activations = ActivationMgr.count()
    users_with_bookmarks = BmarkMgr.count(distinct_users=True)
    return _api_response(request, {
        'count': user_count,
        'activations': pending_activations,
        'with_bookmarks': users_with_bookmarks
    })


@view_config(route_name="api_bookmark_stats", renderer="jsonp")
def bookmark_stats(request):
    """Return all the bookmark stats"""
    bookmark_count = BmarkMgr.count()
    unique_url_count = BmarkMgr.count(distinct=True)
    search = get_fulltext_handler(None)

    return _api_response(request, {
        'count': bookmark_count,
        'unique_count': unique_url_count,
        'in_fulltext': search.doc_count()
    })


@view_config(route_name="api_ping", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def ping(request):
    """Verify that you've setup your api correctly and verified

    """
    rdict = request.matchdict
    params = request.params
    username = rdict.get('username', None)
    api_key = params.get('api_key', None)
    user = UserMgr.get(username=username)
    # Check if user provided the correct api_key
    if api_key == user.api_key:
        return _api_response(request, {
            'success': True,
            'message': 'Looks good'
        })
    else:
        return _api_response(request, {
            'success': False,
            'message': 'API key is invalid.'
        })


@view_config(route_name="api_ping_missing_user", renderer="jsonp")
def ping_missing_user(request):
    """You ping'd but were missing the username in the url for some reason.

    """
    return _api_response(request, {
        'success': False,
        'message': 'Missing username in your api url.'
    })


@view_config(route_name="api_ping_missing_api", renderer="jsonp")
def ping_missing_api(request):
    """You ping'd but didn't specify the actual api url.

    """
    return _api_response(request, {
        'success': False,
        'message': 'The API url should be /api/v1'
    })


@view_config(route_name="api_bmark_hash", renderer="jsonp")
@api_auth('api_key', UserMgr.get, anon=True)
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
    title = params.get('description', None)
    url = params.get('url', None)
    if username:
        username = username.lower()

    # The hash id will always be there or the route won't match.
    bookmark = BmarkMgr.get_by_hash(hash_id, username=username)

    if request.user:
        request_username = request.user.username
    else:
        request_username = None

    if bookmark and not bookmark.has_access(request_username):
        bookmark = None

    # tag_list is a set - no duplicates
    tag_list = set()

    if title or url:
        suggested_tags = suggest_tags(url)
        suggested_tags.update(suggest_tags(title))
        tag_list.update(suggested_tags)

    if bookmark is None:
        request.response.status_int = 404
        ret = {'error': "Bookmark for hash id {0} not found".format(hash_id)}
        # Pack the response with Suggested Tags.
        resp_tags = {'tag_suggestions': list(tag_list)}
        ret.update(resp_tags)
        return _api_response(request, ret)
    else:
        return_obj = dict(bookmark)
        return_obj['tags'] = [dict(tag[1]) for tag in bookmark.tags.items()]

        if 'with_content' in params and params['with_content'] != 'false':
            if bookmark.readable:
                return_obj['readable'] = dict(bookmark.readable)
        # Pack the response with Suggested Tags.
        ret = {
            'bmark': return_obj,
            'tag_suggestions': list(tag_list)
        }
        return _api_response(request, ret)


def _update_mark(mark, params):
    """Update the bookmark found with settings passed in"""
    description = params.get('description', None)
    if not description and mark:
        description = mark.description

    mark.description = description
    mark.extended = params.get('extended', mark.extended)
    mark.is_private = asbool(params.get('is_private', False))

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


@view_config(route_name="api_bmark_add", renderer="jsonp")
@view_config(route_name="api_bmark_update", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def bmark_add(request):
    """Add a new bookmark to the system"""
    rdict = request.matchdict
    try:
        if 'url' in request.params or 'hash_id' in request.params:
            params = request.params
        elif 'url' in request.json_body or 'hash_id' in request.json_body:
            params = request.json_body
        else:
            raise ValueError('No url provided')
    except ValueError:
        request.response.status_int = 400
        return _api_response(request, {
            'error': 'Bad Request: No url provided'
        })

    user = request.user

    if 'url' not in params and 'hash_id' not in rdict:
        request.response.status_int = 400
        return _api_response(request, {
            'error': 'Bad Request: missing url',
        })

    elif 'hash_id' in rdict:
        try:
            mark = BmarkMgr.get_by_hash(
                rdict['hash_id'],
                username=user.username
            )

        except NoResultFound:
            mark = None

        if mark:
            mark = _update_mark(mark, params)
        else:
            request.response.status_code = 404
            return _api_response(request, {
                'error': 'Bookmark with hash id {0} not found.'.format(
                         rdict['hash_id'])
            })

    else:
        # Check if we already have this bookmark.
        try:
            mark = BmarkMgr.get_by_url(params['url'],
                                       username=user.username)

        except NoResultFound:
            mark = None

        if mark:
            mark = _update_mark(mark, params)
        else:
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
            inserted_by = params.get('inserted_by', u'unknown_api')

            mark = BmarkMgr.store(
                params['url'],
                user.username,
                params.get('description', u''),
                params.get('extended', u''),
                params.get('tags', u''),
                dt=stored_time,
                inserted_by=inserted_by,
                is_private=asbool(params.get('is_private', False)),
            )

        # we need to process any commands associated as well
        commander = Commander(mark)
        mark = commander.process()

        # if we have content, stick it on the object here
        if 'content' in params:
            content = StringIO(params['content'])
            content.seek(0)
            parsed = ReadContent.parse(content,
                                       content_type=u"text/html",
                                       url=mark.hashed.url)

            mark.readable = Readable()
            mark.readable.content = parsed.content
            mark.readable.content_type = parsed.content_type
            mark.readable.status_code = parsed.status
            mark.readable.status_message = parsed.status_message

        # we need to flush here for new tag ids, etc
        DBSession.flush()

        mark_data = dict(mark)
        mark_data['tags'] = [dict(mark.tags[tag]) for tag in mark.tags.keys()]

        return _api_response(request, {
            'bmark': mark_data,
            'location': request.route_url('bmark_readable',
                                          hash_id=mark.hash_id,
                                          username=user.username),
        })


@view_config(route_name="api_bmark_remove", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def bmark_remove(request):
    """Remove this bookmark from the system"""
    rdict = request.matchdict
    user = request.user

    try:
        bmark = BmarkMgr.get_by_hash(rdict['hash_id'],
                                     username=user.username)
        DBSession.delete(bmark)
        return _api_response(request, {
            'message': "done",
        })

    except NoResultFound:
        request.response.status_code = 404
        return _api_response(request, {
            'error': 'Bookmark with hash id {0} not found.'.format(
                     rdict['hash_id'])
        })


@view_config(route_name="api_bmarks", renderer="jsonp")
@view_config(route_name="api_bmarks_user", renderer="jsonp")
@view_config(route_name="api_bmarks_tags", renderer="jsonp")
@view_config(route_name="api_bmarks_user_tags", renderer="jsonp")
@api_auth('api_key', UserMgr.get, anon=True)
def bmark_recent(request, with_content=False):
    """Get a list of the bmarks for the api call"""
    rdict = request.matchdict
    params = request.params

    # check if we have a page count submitted
    page = int(params.get('page', '0'))
    count = int(params.get('count', RESULTS_MAX))
    if not with_content:
        with_content = asbool(params.get('with_content', False))

    # we only want to do the username if the username is in the url
    username = rdict.get('username', None)
    if username:
        username = username.lower()

    # We need to check who has requested for the bookmarks.
    if request.user:
        requested_by = request.user.username
    else:
        requested_by = None

    # We need to check if we have an ordering crtieria specified.
    order_by = params.get('sort', None)
    if order_by == "popular":
        if username:
            order_by = Bmark.clicks.desc()
        else:
            order_by = Hashed.clicks.desc()

    else:
        order_by = Bmark.stored.desc()

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

    # @todo fix this!
    # if we allow showing of content the query hangs and fails on the
    # postgres side. Need to check the query and figure out what's up.
    # see bug #142
    recent_list = BmarkMgr.find(
        limit=count,
        order_by=order_by,
        page=page,
        tags=tags,
        username=username,
        with_tags=True,
        with_content=with_content,
        requested_by=requested_by,
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

    return _api_response(request, {
        'bmarks': result_set,
        'max_count': RESULTS_MAX,
        'count': len(recent_list),
        'page': page,
        'tag_filter': tags,
    })


@view_config(route_name="api_count_bmarks_user", renderer="jsonp")
@api_auth('api_key', UserMgr.get, anon=False)
def user_bmark_count(request):
    """Get the user's daily bookmark total for the given time window"""
    params = request.params

    username = request.user.username
    start_date = params.get('start_date', None)
    end_date = params.get('end_date', None)
    bmark_count_list = StatBookmarkMgr.count_user_bmarks(
        username=username,
        start_date=start_date,
        end_date=end_date
    )

    result_set = []
    for res in bmark_count_list[0]:
        return_obj = dict(res)

        result_set.append(return_obj)
    return _api_response(request, {
        'count': result_set,
        'start_date': str(bmark_count_list[1]),
        'end_date': str(bmark_count_list[2])
    })


@view_config(route_name="api_bmarks_export", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def bmark_export(request):
    """Export via the api call to json dump

    """
    username = request.user.username

    bmark_list = BmarkMgr.user_dump(username, username)
    # log that the user exported this
    BmarkLog.export(username, username)

    def build_bmark(bmark):
        d = dict(bmark)
        d['hashed'] = dict(bmark.hashed)
        return _api_response(request, d)

    return _api_response(request, {
        'bmarks': [build_bmark(bmark) for bmark in bmark_list],
        'count': len(bmark_list),
        'date': str(datetime.utcnow())
    })


@view_config(route_name="api_extension_sync", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def extension_sync(request):
    """Return a list of the bookmarks we know of in the system

    For right now, send down a list of hash_ids

    """
    username = request.user.username

    hash_list = BmarkMgr.hash_list(username=username)
    return _api_response(request, {
        'hash_list': [hash[0] for hash in hash_list]
    })


@view_config(route_name="api_bmark_search", renderer="jsonp")
@view_config(route_name="api_bmark_search_user", renderer="jsonp")
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

    username = mdict.get('username', None)
    if request.user:
        requested_by = request.user.username
    else:
        requested_by = None

    # with content is always in the get string
    search_content = asbool(rdict.get('with_content', False))

    conn_str = request.registry.settings.get('sqlalchemy.url', False)
    searcher = get_fulltext_handler(conn_str)

    # check if we have a page count submitted
    page = rdict.get('page', 0)
    count = rdict.get('count', 10)

    try:
        res_list = searcher.search(
            phrase,
            content=search_content,
            username=username,
            requested_by=requested_by,
            ct=count,
            page=page
        )
    except ValueError:
        request.response.status_int = 404
        ret = {'error': "Bad Request: Page number out of bound"}
        return _api_response(request, ret)

    constructed_results = []
    for res in res_list:
        return_obj = dict(res)
        return_obj['tags'] = [dict(tag[1]) for tag in res.tags.items()]

        # the hashed object is there as well, we need to pull the url and
        # clicks from it as total_clicks
        return_obj['url'] = res.hashed.url
        return_obj['total_clicks'] = res.hashed.clicks

        constructed_results.append(return_obj)

    return _api_response(request, {
        'search_results': constructed_results,
        'result_count': len(constructed_results),
        'phrase': phrase,
        'page': page,
        'with_content': search_content,
        'username': username,
    })


@view_config(route_name="api_tag_complete", renderer="jsonp")
@view_config(route_name="api_tag_complete_user", renderer="jsonp")
@api_auth('api_key', UserMgr.get, anon=True)
def tag_complete(request):
    """Complete a tag based on the given text

    :@param tag: GET string, tag=sqlalchemy
    :@param current: GET string of tags we already have python+database

    """
    rdict = request.matchdict
    params = request.GET

    username = rdict.get('username', None)
    if username:
        username = username.lower()

    if request.user:
        requested_by = request.user.username
    else:
        requested_by = None

    if username != requested_by:
        request.response.status_int = 403
        return _api_response(request, {})

    if 'current' in params and params['current'] != "":
        current_tags = params['current'].split()
    else:
        current_tags = None

    if 'tag' in params and params['tag']:
        tag = params['tag']

        tags = TagMgr.complete(tag,
                               current=current_tags,
                               username=username,
                               requested_by=requested_by)
    else:
        tags = []

    # reset this for the payload join operation
    if current_tags is None:
        current_tags = []

    return _api_response(request, {
        'current': ",".join(current_tags),
        'tags': [t.name for t in tags]
    })


# USER ACCOUNT INFORMATION CALLS
@view_config(route_name="api_user_account", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def account_info(request):
    """Return the details of the user account specifed

    expecting username in matchdict
    We only return a subset of data. We're not sharing keys such as api_key,
    password hash, etc.

    """
    user = request.user

    return _api_response(request, user.safe_data())


@view_config(route_name="api_user_account_update", renderer="jsonp")
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
        user_acct.email = email.lower()

    if 'email' in json_body and json_body['email'] is not None:
        email = json_body.get('email')
        user_acct.email = email.lower()

    return _api_response(request, user_acct.safe_data())


@view_config(route_name="api_reset_api_key", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def reset_api_key(request):
    """Generate and Return the currently logged in user's new api key

       Callable by either a logged in user or the api key for mobile apps/etc

    """
    user = request.user
    # Generate new api key and assign it to user's api key
    user.api_key = User.gen_api_key()
    return _api_response(request, {
        'api_key': user.api_key,
        'message': 'Api Key was successfully changed',
    })


@view_config(route_name="api_user_api_key", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def api_key(request):
    """Return the currently logged in user's api key

    This api call is available both on the website via a currently logged in
    user and via a valid api key passed into the request. In this way we should
    be able to add this to the mobile view with an ajax call as well as we do
    into the account information on the main site.

    """
    user_acct = request.user
    return _api_response(request, {
        'api_key': user_acct.api_key,
        'username': user_acct.username
    })


@view_config(route_name="api_user_reset_password", renderer="jsonp")
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
    # POST
    if current is None and new is None:
        params = request.json_body
        current = params.get('current_password', None)
        new = params.get('new_password', None)

    user_acct = request.user

    if not UserMgr.acceptable_password(new):
        request.response.status_int = 406
        return _api_response(request, {
            'username': user_acct.username,
            'error': "Come on, let's try a real password this time"
        })

    # before we change the password, let's verify it
    if user_acct.validate_password(current):
        # we're good to change it
        user_acct.password = new
        return _api_response(request, {
            'username': user_acct.username,
            'message': "Password changed",
        })
    else:
        request.response.status_int = 403
        return _api_response(request, {
            'username': user_acct.username,
            'error': "There was a typo somewhere. Please check your request"
        })


@view_config(route_name="api_user_suspend", renderer="jsonp")
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
        return _api_response(request, {
            'error': "Please submit an email address",
        })

    if user is None and email is not None:
        user = UserMgr.get(email=email)

    if user is None:
        request.response.status_int = 404
        return _api_response(request, {
            'error': "Please submit a valid address",
            'email': email
        })

    # check if we've already gotten an activation for this user
    if user.activation is not None:
        request.response.status_int = 406
        return _api_response(request, {
            'error': """You've already marked your account for reactivation.
Please check your email for the reactivation link. Make sure to
check your spam folder.""",
            'username': user.username,
        })

    # mark them for reactivation
    user.reactivate(u"FORGOTTEN")

    # log it
    AuthLog.reactivate(user.username)

    # and then send an email notification
    # @todo the email side of things
    settings = request.registry.settings
    msg = ReactivateMsg(user.email,
                        "Activate your Bookie account",
                        settings)

    msg.send({
        'url': request.route_url(
            'reset',
            username=user.username,
            reset_key=user.activation.code),
        'username': user.username
    })

    return _api_response(request, {
        'message': """Your account has been marked for reactivation. Please
                    check your email for instructions to reset your
                    password""",
    })


@view_config(route_name="api_user_suspend_remove", renderer="jsonp")
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
    new_username = params.get('new_username', None)

    if username is None and activation is None and password is None:
        # then try to get the same fields out of a json body
        json_body = request.json_body
        username = json_body.get('username', None)
        activation = json_body.get('code', None)
        password = json_body.get('password', None)
        new_username = json_body.get('new_username', None)

    if not UserMgr.acceptable_password(password):
        request.response.status_int = 406
        return _api_response(request, {
            'error': "Come on, pick a real password please",
        })

    username = username.lower()
    new_username = new_username.lower() if new_username else None
    res = ActivationMgr.activate_user(
        username,
        activation,
        password)

    if res:
        # success so respond nicely
        AuthLog.reactivate(username, success=True, code=activation)

        # if there's a new username and it's not the same as our current
        # username, update it
        if new_username and new_username != username:
            try:
                user = UserMgr.get(username=username)
                user.username = new_username
            except IntegrityError, exc:
                request.response.status_int = 500
                return _api_response(request, {
                    'error': 'There was an issue setting your new username',
                    'exc': str(exc)
                })

        return _api_response(request, {
            'message': "Account activated, please log in.",
            'username': username,
        })
    else:
        AuthLog.reactivate(username, success=False, code=activation)
        request.response.status_int = 500
        return _api_response(request, {
            'error': "There was an issue attempting to activate this account.",
        })


@view_config(route_name="api_user_invite", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def invite_user(request):
    """Invite a new user into the system.

    :param username: user that is requested we invite someone
    :param email: email address of the new user

    """
    params = request.params

    email = params.get('email', None)
    user = request.user

    if not email:
        # try to get it from the json body
        email = request.json_body.get('email', None)

    if not email:
        # if still no email, I give up!
        request.response.status_int = 406
        return _api_response(request, {
            'username': user.username,
            'error': "Please submit an email address"
        })

    email = email.lower()
    # first see if the user is already in the system
    exists = UserMgr.get(email=email.lower())
    if exists:
        request.response.status_int = 406
        return _api_response(request, {
            'username': exists.username,
            'error': "This user is already a Bookie user!"
        })

    new_user = user.invite(email.lower())
    if new_user:
        LOG.debug(new_user.username)
        # then this user is able to invite someone
        # log it
        AuthLog.reactivate(new_user.username)

        # and then send an email notification
        # @todo the email side of things
        settings = request.registry.settings
        msg = ActivationMsg(new_user.email,
                            "Enable your Bookie account",
                            settings)

        msg.send(
            request.route_url(
                'reset',
                username=new_user.username,
                reset_key=new_user.activation.code))
        return _api_response(request, {
            'message': 'You have invited: ' + new_user.email
        })
    else:
        # you have no invites
        request.response.status_int = 406
        return _api_response(request, {
            'username': user.username,
            'error': "You have no invites left at this time."
        })


@view_config(route_name="api_social_connections", renderer="jsonp")
@api_auth('api_key', UserMgr.get)
def social_connections(request):
    rdict = request.matchdict
    username = rdict.get('username', None)
    res = [dict(con) for con in SocialMgr.get_all_connections(username)]
    return _api_response(request, {'count': len(res),
                                   'social_connections': res})


@view_config(route_name="api_admin_readable_todo", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def to_readable(request):
    """Get a list of urls, hash_ids we need to readable parse"""
    url_list = Bmark.query.outerjoin(Readable, Readable.bid == Bmark.bid).\
        join(Bmark.hashed).\
        options(contains_eager(Bmark.hashed)).\
        filter(Readable.imported.is_(None)).all()

    def data(urls):
        """Yield out the results with the url in the data streamed."""
        for url in urls:
            d = dict(url)
            d['url'] = url.hashed.url
            yield d

    return _api_response(request, {
        'urls': [u for u in data(url_list)]
    })


@view_config(route_name="api_admin_twitter_refresh", renderer="jsonp")
@view_config(route_name="api_admin_twitter_refresh_all", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def twitter_refresh(request):
    """Update tweets fetched from user account """
    mdict = request.matchdict
    username = mdict.get('username', None)
    tasks.process_twitter_connections(username)
    ret = {
        'success': True,
        'message': "running bot to fetch user's tweets"
    }
    return _api_response(request, ret)


@view_config(route_name="api_admin_readable_reindex", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def readable_reindex(request):
    """Force the fulltext index to rebuild

    This loops through ALL bookmarks and might take a while to complete.

    """
    tasks.reindex_fulltext_allbookmarks.delay()
    return _api_response(request, {
        'success': True
    })


@view_config(route_name="api_admin_accounts_inactive", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def accounts_inactive(request):
    """Return a list of the accounts that aren't activated."""
    user_list = UserMgr.get_list(active=False)
    ret = {
        'count': len(user_list),
        'users': [dict(h) for h in user_list],
    }
    return _api_response(request, ret)


@view_config(route_name="api_admin_accounts_invites", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def accounts_invites(request):
    """Return a list of the accounts that aren't activated."""
    user_list = UserMgr.get_list()
    ret = {
        'users': [(u.username, u.invite_ct) for u in user_list],
    }
    return _api_response(request, ret)


@view_config(route_name="api_admin_accounts_invites_add", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def accounts_invites_add(request):
    """Set the number of invites a user has available.

    :matchdict username: The user to give these invites to.
    :matchdict count: The number of invites to give them.
    """
    rdict = request.matchdict
    username = rdict.get('username', None)
    if username:
        username = username.lower()
    count = rdict.get('count', None)

    if username is not None and count is not None:
        user = UserMgr.get(username=username)

        if user:
            user.invite_ct = count
            return _api_response(request, dict(user))
        else:
            request.response.status_int = 404
            ret = {'error': "Invalid user account."}
            return _api_response(request, ret)
    else:
        request.response.status_int = 400
        ret = {'error': "Bad request, missing parameters"}
        return _api_response(request, ret)


@view_config(route_name="api_admin_imports_list", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def import_list(request):
    """Provide some import related data."""
    import_list = ImportQueueMgr.get_list()
    ret = {
        'count': len(import_list),
        'imports': [dict(h) for h in import_list],
    }
    return _api_response(request, ret)


@view_config(route_name="api_admin_imports_reset", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def import_reset(request):
    """Reset an import to try again"""
    rdict = request.matchdict
    import_id = rdict.get('id', None)

    if not id:
        request.response.status_int = 400
        ret = {'error': "Bad request, missing parameters"}
        return _api_response(request, ret)

    imp = ImportQueueMgr.get(int(import_id))
    imp.status = 0
    tasks.importer_process.delay(imp.id)

    ret = {
        'import': dict(imp)
    }
    return _api_response(request, ret)


@view_config(route_name="api_admin_users_list", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def user_list(request):
    """Provide list of users in the system.

    Supported Query params: order, limit
    """
    params = request.params
    order = params.get('order', None)
    limit = params.get('limit', None)
    user_list = UserMgr.get_list(order=order, limit=limit)
    ret = {
        'count': len(user_list),
        'users': [dict(h) for h in user_list],
    }
    return _api_response(request, ret)


@view_config(route_name="api_admin_new_user", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def new_user(request):
    """Add a new user to the system manually."""
    rdict = request.params

    u = User()

    u.username = unicode(rdict.get('username'))
    if u.username:
        u.username = u.username.lower()
    u.email = unicode(rdict.get('email')).lower()
    passwd = get_random_word(8)
    u.password = passwd
    u.activated = True
    u.is_admin = False
    u.api_key = User.gen_api_key()

    try:
        DBSession.add(u)
        DBSession.flush()
        # We need to return the password since the admin added the user
        # manually.  This is only time we should have/give the original
        # password.
        ret = dict(u)
        ret['random_pass'] = passwd
        return _api_response(request, ret)

    except IntegrityError, exc:
        # We might try to add a user that already exists.
        LOG.error(exc)
        request.response.status_int = 400
        return _api_response(request, {
            'error': 'Bad Request: User exists.',
        })


@view_config(route_name="api_admin_del_user", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def del_user(request):
    """Remove a bad user from the system via the api.

    For admin use only.

    Removes all of a user's bookmarks before removing the user.

    """
    mdict = request.matchdict

    # Submit a username.
    del_username = mdict.get('username', None)

    if del_username is None:
        LOG.error('No username to remove.')
        request.response.status_int = 400
        return _api_response(request, {
            'error': 'Bad Request: No username to remove.',
        })

    u = UserMgr.get(username=del_username)

    if not u:
        LOG.error('Username not found.')
        request.response.status_int = 404
        return _api_response(request, {
            'error': 'User not found.',
        })

    try:
        # First delete all the tag references for this user's bookmarks.
        res = DBSession.query(Bmark.bid).filter(Bmark.username == u.username)
        bids = [b[0] for b in res]

        qry = bmarks_tags.delete(bmarks_tags.c.bmark_id.in_(bids))
        qry.execute()

        # Delete all of the bmarks for this year.
        Bmark.query.filter(Bmark.username == u.username).delete()
        DBSession.delete(u)
        return _api_response(request, {
            'success': True,
            'message': 'Removed user: ' + del_username
        })
    except Exception, exc:
        # There might be cascade issues or something that causes us to fail in
        # removing.
        LOG.error(exc)
        request.response.status_int = 500
        return _api_response(request, {
            'error': 'Bad Request: ' + str(exc)
        })


@view_config(route_name="api_admin_bmark_remove", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def admin_bmark_remove(request):
    """Remove this bookmark from the system"""
    rdict = request.matchdict
    username = rdict.get('username')
    if username:
        username = username.lower()
    hash_id = rdict.get('hash_id')

    try:
        bmark = BmarkMgr.get_by_hash(hash_id,
                                     username=username)
        print bmark
        if bmark:
            DBSession.delete(bmark)
            return _api_response(request, {
                'message': "done",
            })
        else:
            return _api_response(request, {
                'error': 'Bookmark not found.',
            })

    except NoResultFound:
        request.response.status_code = 404
        return _api_response(request, {
            'error': 'Bookmark with hash id {0} not found.'.format(
                rdict['hash_id'])
        })


@view_config(route_name="api_admin_applog", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def admin_applog(request):
    """Return applog data for admin use."""
    rdict = request.GET

    # Support optional filter parameters
    days = int(rdict.get('days', 1))
    status = rdict.get('status', None)
    message = rdict.get('message', None)

    log_list = AppLogMgr.find(
        days=days,
        message_filter=message,
        status=status,
    )

    ret = {
        'count': len(log_list),
        'logs': [dict(l) for l in log_list],
    }
    return _api_response(request, ret)


@view_config(route_name="api_admin_non_activated", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def admin_non_activated(request):
    """Return non activated account details"""
    ret = []
    res = UserMgr.non_activated_account()
    if res:
        ret = [u.username for u in res]

    return _api_response(request, {
        'count': len(ret),
        'status': True,
        'data': ret,
    })


@view_config(route_name="api_admin_delete_non_activated", renderer="jsonp")
@api_auth('api_key', UserMgr.get, admin_only=True)
def admin_delete_non_activated(request):
    """Delete non activated accounts"""
    UserMgr.non_activated_account(delete=True)
    return _api_response(request, {
        'status': True,
        'message': 'Removed non activated accounts'
    })
