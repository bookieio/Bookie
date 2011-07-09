import logging

from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.security import remember
from pyramid.security import forget
from pyramid.url import route_url
from pyramid.view import view_config

from bookie.lib.applog import AuthLog
from bookie.models.auth import UserMgr
from bookie.models.auth import ActivationMgr


LOG = logging.getLogger(__name__)


@view_config(route_name="login", renderer="/auth/login.mako")
def login(request):
    """Login the user to the system

    If not POSTed then show the form
    If error, display the form with the error message
    If successful, forward the user to their /recent

    Note: the came_from stuff we're not using atm. We'll clean out if we keep
    things this way

    """
    login_url = route_url('login', request)
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)

    message = ''
    login = ''
    password = ''

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']

        LOG.debug(login)
        auth = UserMgr.get(username=login)
        LOG.debug(auth)
        LOG.debug(UserMgr.get_list())

        if auth and auth.validate_password(password) and auth.activated:
            # We use the Primary Key as our identifier once someone has authenticated rather than the
            # username.  You can change what is returned as the userid by altering what is passed to
            # remember.
            headers = remember(request, auth.id, max_age='86400')
            auth.last_login = datetime.now()

            # log the successful login
            AuthLog.login(login, True)

            # we're always going to return a user to their own /recent after a
            # login
            return HTTPFound(location=request.route_url('user_bmark_recent',
                                                        username=auth.username),
                             headers=headers)

        # log the right level of problem
        if auth and not auth.validate_password(password):
            message = "Failed login"
            AuthLog.login(login, False, password=password)

        elif auth and not auth.activated:
            message = "User account deactivated. Please check your email."
            AuthLog.login(login, False, password=password)
            AuthLog.disabled(login)

        elif auth is None:
            message = "Failed login"
            AuthLog.login(login, False, password=password)

    return {
        'message': message,
        'came_from':  came_from,
        'login':  login,
        'password':  password,
    }


@view_config(route_name="logout", renderer="/auth/login.mako")
def logout(request):
    headers = forget(request)
    return HTTPFound(location = route_url('home', request),
                     headers = headers)


@view_config(route_name="api_user_reactivate", renderer="morjson")
def reactivate(request):
    """Reset a user account to enable them to change their password"""
    params = request.params

    # we need to get the user from the email
    email = params.get('email', None)

    if email is None:
        return {
            'success': False,
            'message':  "Please submit an email address",
            'payload': {},
        }

    user = UserMgr.get(email=email)
    if user is None:
        return {
            'success': False,
            'message':  "Please submit a valid address",
            'payload': {},
        }

    # mark them for reactivation
    user.reactivate("FORGOTTEN")

    # log it
    AuthLog.reactivate(user.username)

    # and then send an email notification
    # @todo the email side of things
    return {
        'success': True,
        'message':  """Your account has been marked for reactivation. Please
                    check your email for instructions to reset your
                    password""",
        'payload': {},
    }


@view_config(route_name="reset", renderer="/auth/reset.mako")
def reset(request):
    """Once deactivated, allow for changing the password via activation key"""
    rdict = request.matchdict

    username = rdict.get('username', None)
    activation_key = rdict.get('reset_key', None)

    # this can only be visited if user is visiting the reset with the right key
    # for the username in the url
    user = ActivationMgr.get_user(username, activation_key)

    if user is None:
        # just 404 if we don't have an activation code for this user
        raise HTTPNotFound()

    return {
        'user': user,
    }


def forbidden_view(request):
    login_url = route_url('login', request)
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    return render_to_response('/auth/login.mako', dict(
               message = '',
               url = request.application_url + '/login',
               came_from = came_from,
               login = '',
               password = '',
           ), request=request)
