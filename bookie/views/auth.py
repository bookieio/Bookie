import logging

from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.security import remember
from pyramid.security import forget
from pyramid.url import route_url
from pyramid.view import view_config

from bookie.lib.applog import AuthLog
from bookie.models.auth import UserMgr


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

        if auth and auth.validate_password(password):
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

        message = 'Failed login'
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
