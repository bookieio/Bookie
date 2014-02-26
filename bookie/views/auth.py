import logging

from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.security import remember
from pyramid.security import forget
from pyramid.url import route_url
from pyramid.view import view_config

from bookie.bcelery import tasks
from bookie.lib.applog import AuthLog
from bookie.models import IntegrityError
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
        referrer = u'/'  # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)

    message = u''
    login = u''
    password = u''

    if 'form.submitted' in request.params:
        login = request.params['login'].lower()
        password = request.params['password']

        LOG.debug(login)
        auth = UserMgr.get(username=login)
        LOG.debug(auth)
        LOG.debug(UserMgr.get_list())

        if auth and auth.validate_password(password) and auth.activated:
            # We use the Primary Key as our identifier once someone has
            # authenticated rather than the username.  You can change what is
            # returned as the userid by altering what is passed to remember.
            headers = remember(request, auth.id, max_age=60 * 60 * 24 * 30)
            auth.last_login = datetime.utcnow()

            # log the successful login
            AuthLog.login(login, True)

            # we're always going to return a user to their own /recent after a
            # login
            return HTTPFound(
                location=request.route_url(
                    'user_bmark_recent',
                    username=auth.username),
                headers=headers)

        # log the right level of problem
        if auth and not auth.validate_password(password):
            message = "Your login attempt has failed."
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
        'came_from': came_from,
        'login': login,
        'password': password,
    }


@view_config(route_name="logout", renderer="/auth/login.mako")
def logout(request):
    headers = forget(request)
    return HTTPFound(location=route_url('home', request),
                     headers=headers)


@view_config(route_name="signup", renderer="/auth/signup.mako")
def signup(request):
    """Signup merely shows the signup for to users.

    We always take their signup even if we don't send out the email/invite at
    this time so that we can stage invites across a specific number in waves.

    """
    return {}


@view_config(route_name="signup_process", renderer="/auth/signup.mako")
def signup_process(request):
    """Process the signup request

    If there are any errors drop to the same template with the error
    information.

    """
    params = request.params
    email = params.get('email', None)

    if not email:
        # if still no email, I give up!
        return {
            'errors': {
                'email': 'Please supply an email address to sign up.'
            }
        }

    # first see if the user is already in the system
    exists = UserMgr.get(email=email)
    if exists:
        return {
            'errors': {
                'email': 'The user has already signed up.'
            }
        }

    new_user = UserMgr.signup_user(email, 'signup')
    if new_user:
        # then this user is able to invite someone
        # log it
        AuthLog.reactivate(new_user.username)

        # and then send an email notification
        # @todo the email side of things
        settings = request.registry.settings

        # Add a queue job to send the user a notification email.
        tasks.email_signup_user.delay(
            new_user.email,
            "Enable your Bookie account",
            settings,
            request.route_url(
                'reset',
                username=new_user.username,
                reset_key=new_user.activation.code
            )
        )

        # And let the user know they're signed up.
        return {
            'message': 'Thank you for signing up from: ' + new_user.email
        }
    else:
        return {
            'errors': {
                'email': 'There was an unknown error signing up.'
            }
        }


@view_config(route_name="reset", renderer="/auth/reset.mako")
def reset(request):
    """Once deactivated, allow for changing the password via activation key"""
    rdict = request.matchdict
    params = request.params

    # This is an initial request to show the activation form.
    username = rdict.get('username', None)
    activation_key = rdict.get('reset_key', None)
    user = ActivationMgr.get_user(username, activation_key)

    if user is None:
        # just 404 if we don't have an activation code for this user
        raise HTTPNotFound()

    if 'code' in params:
        # This is a posted form with the activation, attempt to unlock the
        # user's account.
        username = params.get('username', None)
        activation = params.get('code', None)
        password = params.get('new_password', None)
        new_username = params.get('new_username', None)
        error = None

        if not UserMgr.acceptable_password(password):
            # Set an error message to the template.
            error = "Come on, pick a real password please."
        else:
            res = ActivationMgr.activate_user(username, activation, password)
            if res:
                # success so respond nicely
                AuthLog.reactivate(username, success=True, code=activation)

                # if there's a new username and it's not the same as our
                # current username, update it
                if new_username and new_username != username:
                    try:
                        user = UserMgr.get(username=username)
                        user.username = new_username
                    except IntegrityError:
                        error = 'There was an issue setting your new username'
            else:
                AuthLog.reactivate(username, success=False, code=activation)
                error = ('There was an issue attempting to activate'
                         'this account.')

        if error:
            return {
                'message': error,
                'user': user
            }
        else:
            # Log the user in and move along.
            headers = remember(request, user.id, max_age=60 * 60 * 24 * 30)
            user.last_login = datetime.utcnow()

            # log the successful login
            AuthLog.login(user.username, True)

            # we're always going to return a user to their own /recent after a
            # login
            return HTTPFound(
                location=request.route_url(
                    'user_bmark_recent',
                    username=user.username),
                headers=headers)

    else:
        LOG.error("CHECKING")
        LOG.error(username)

        if user is None:
            # just 404 if we don't have an activation code for this user
            raise HTTPNotFound()

        LOG.error(user.username)
        LOG.error(user.email)
        return {
            'user': user,
        }


def forbidden_view(request):
    login_url = route_url('login', request)
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    return render_to_response(
        '/auth/login.mako',
        dict(
            message='',
            url=request.application_url + '/login',
            came_from=came_from,
            login='',
            password='',
        ),
        request=request)
