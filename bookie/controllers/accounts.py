import logging

from pylons import config, request, response, tmpl_context as tpl, url
from pylons.decorators import validate
from pylons.controllers.util import abort, redirect
from bookie.lib.base import BaseController, render

from bookie.model.auth import User, UserMgr, GroupMgr

from repoze.what.predicates import not_anonymous, in_group
from repoze.what.plugins.pylonshq import ActionProtector

from morpylons.lib.jsonresponse import mijson
from morpylons.lib.ldaputils import LDAPNotFound, LDAPSearch
from morpylons.lib import auth

from bookie.validation import UserFormNew, error_formatter
from bookie.model import meta

log = logging.getLogger(__name__)


class AccountsController(BaseController):
    """Controller for Accounts """

    def index(self):
        """ Default to the account edit for your account? """
        abort(404)

    def login(self):
        """This is where the login form should be rendered."""
        if auth.check(not_anonymous()):
            # if we're not anonymous then we're logged in and need to be
            # redirected
            log.debug('already logged in')
            redirect(url('/page/test'))

        # Without the login counter, we won't be able to tell if the user has
        # tried to log in with the wrong credentials
        if 'repoze.who.logins' in request.environ:
            login_counter = request.environ['repoze.who.logins']
        else:
            login_counter = 0

        if login_counter > 0:
            log.debug('Wrong Login credentials')
            #flash('Wrong credentials')
        tpl.login_counter = login_counter
        tpl.came_from = request.params.get('came_from') or url('/')

        if 'login_failed' in request.params:
            tpl.login_failed = True
        else:
            tpl.login_failed = False
        return render('/login.mako')

    def post_login(self):
        """ Handle logic post a user's login

        I want to create a login_handler that's redirected to after login. This
        would check

        - if user was logged in, if not then send back to login
        - if user is admin, go to job list
        - if user can add joblist then go to *
        - if user is read only go to job list that's trimmed down a bit

        On the post login page adjust the max age on the existing cookie to XX
        remember me timeframe
        """
        if auth.check(not_anonymous()):
            log.debug('checked auth')
        else:
            # login failed, redirect back to login
            log.debug('failed auth')
            redirect(url(controller="accounts",
                action="login",
                login_failed=True)
            )

        # expire this cookie into the future
        ck = request.cookies['authtkt']
        response.set_cookie('authtkt', ck,
                max_age=60 * 60 * 24 * 7,
                path='/'
        )

        redirect(url('/page/test'))

    @ActionProtector(in_group('admin'))
    def list(self):
        """ List the user accounts in the system"""
        user_list = UserMgr.get_list()
        log.debug(user_list)
        tpl.user_list = user_list

        return render('/account/list.mako')

    @ActionProtector(in_group('admin'))
    @mijson()
    def edit(self, user_name):
        """Load the edit ui for this user"""
        tpl.user = UserMgr.get(user_name=user_name)
        tpl.group_list = GroupMgr.get_list()

        tpl.form_errors = False
        for g in tpl.group_list:
            if g in tpl.user.groups:
                log.debug("IN GROUP")
            else:
                log.debug("NOT IN GROUP")

        self.json.success = True
        return render('/account/edit.mako')

    @ActionProtector(in_group('admin'))
    @mijson()
    def edit_error(self):
        """Authenticate the changes to the user account specified

        Currently the only changes to a user account are to assign permission
        groups to it.

        """
        user_groups = request.params.getall('groups')
        user_name = request.params['user_name']

        user = UserMgr.get(user_name=user_name)

        # we're admin so we're allowed to do this regardless of username
        user.groups = GroupMgr.get_list(user_groups)
        redirect(url(controller="accounts", action="list"))

    def new(self):
        """Add a new user to the auth system

        """
        tpl.group_list = GroupMgr.get_list()
        tpl.form_errors = False
        return render('/account/new.mako')

    @validate(schema=UserFormNew(), form='new', post_only=False, on_get=True,
        auto_error_formatter=error_formatter, prefix_error=False)
    def new_errors(self):
        """Validate a new user account details

        """
        user = User()
        user.fromdict(request.params)

        # now make sure we create the group info
        # this just overwrites the from dict stuff I think
        user_groups = request.params.getall('groups')
        user.groups = GroupMgr.get_list(user_groups)

        try:
            meta.Session.add(user)
            #SystemLogger.log_activity('system',
            #        None,
            #        'Added new user: %s to the system' % user.user_name)

        except:
            meta.Session.rollback()

        # @todo fill in the code to create the queued job to process this
        # new file we just uploaded with tons of emails to create
        redirect(url(controller="accounts", action="list"))

    @ActionProtector(in_group('admin'))
    @mijson()
    def delete(self, user_name):
        """Remove a user from the system if this is an admin

        :param user_name: the user to remove from the system

        """
        user = UserMgr.get(user_name=user_name)
        meta.Session.delete(user)
        redirect(url(controller="accounts", action="list"))

    @ActionProtector(in_group('admin'))
    @mijson()
    def fetch_ldap_user(self, user_name):
        """ Attempt to find this user in the ldap database and return the user
        object

        :param id: string username or email address

        """
        ldap_server = config['app_conf']['auth.ldap_server']
        search = LDAPSearch(ldap_server)

        if user_name is None or user_name == "":
            self.json.success = False
            self.json.message = "Please supply a user name or email address"

        try:
            # see if this is an email search
            record = search.find_by_email(user_name)
            self.json.success = True
            self.json.payload = {'user': record.attributes}
        except LDAPNotFound:
            # if we fail to find the user by their email, just try it on the
            # cn:username
            try:
                record = search.find_by_cn(user_name)
                self.json.success = True
                self.json.payload = {'user': record.attributes}
            except LDAPNotFound:
                self.json.success = False
                self.json.message = "User %s not found in ldap system" % \
                    user_name

        if self.json.success:
            self.json.message = "Found user in the system as: %s" % \
                record.attributes['fullName']

        log.debug(self.json.payload)
        return self.json.message
