"""
Sample SQLAlchemy-powered model definition for the repoze.what SQL plugin.

This model definition has been taken from a quickstarted TurboGears 2 project,
but it's absolutely independent of TurboGears.

"""

import bcrypt
import hashlib
import logging
import random

from datetime import (
    datetime,
    timedelta,
)

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Boolean

from sqlalchemy.orm import relation
from sqlalchemy.orm import synonym

from bookie.models import Base
from bookie.models import DBSession
from bookie.models.social import BaseConnection

LOG = logging.getLogger(__name__)
GROUPS = ['admin', 'user']
ACTIVATION_AGE = timedelta(days=3)
NON_ACTIVATION_AGE = timedelta(days=30)


def get_random_word(wordLen):
    word = ''
    for i in xrange(wordLen):
        word += random.choice(('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrs'
                               'tuvwxyz0123456789/&='))
    return word


class ActivationMgr(object):

    @staticmethod
    def count():
        """Count how many activations are in the system."""
        return Activation.query.count()

    @staticmethod
    def get_user(username, code):
        """Get the user for this code"""
        qry = Activation.query.\
            filter(Activation.code == code).\
            filter(User.username == username)

        res = qry.first()

        if res is not None:
            return res.user
        else:
            return None

    @staticmethod
    def activate_user(username, code, new_pass):
        """Given this code get the user with this code make sure they exist"""

        qry = Activation.query.\
            filter(Activation.code == code).\
            filter(User.username == username)

        res = qry.first()

        if UserMgr.acceptable_password(new_pass) and res is not None:
            user = res.user
            user.activated = True
            user.password = new_pass
            res.activate()

            LOG.debug(dict(user))

            return True
        else:
            return None


class Activation(Base):
    """Handle activations/password reset items for users

    The id is the user's id. Each user can only have one valid activation in
    process at a time

    The code should be a random hash that is valid only one time
    After that hash is used to access the site it'll be removed

    The created by is a system: new user registration, password reset, forgot
    password, etc.

    """
    __tablename__ = u'activations'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    code = Column(Unicode(60))
    valid_until = Column(
        DateTime,
        default=lambda: datetime.utcnow + ACTIVATION_AGE)
    created_by = Column('created_by', Unicode(255))

    def __init__(self, created_system):
        """Create a new activation"""
        self.code = Activation._gen_activation_hash()
        self.created_by = created_system
        self.valid_until = datetime.utcnow() + ACTIVATION_AGE

    @staticmethod
    def _gen_activation_hash():
        """Generate a random activation hash for this user account"""
        # for now just cheat and generate an api key, that'll work for now
        return User.gen_api_key()

    def activate(self):
        """Remove this activation"""
        DBSession.delete(self)


class UserMgr(object):
    """ Wrapper for static/combined operations of User object"""

    @staticmethod
    def count():
        """Number of users in the system."""
        return User.query.count()

    @staticmethod
    def non_activated_account(delete=False):
        """Get a list of  user accounts which are not verified since
        30 days of signup"""
        test_date = datetime.utcnow() - NON_ACTIVATION_AGE
        query = DBSession.query(Activation.id).\
            filter(Activation.valid_until < test_date).\
            subquery(name="query")
        qry = DBSession.query(User).\
            filter(User.activated.is_(False)).\
            filter(User.last_login.is_(None)).\
            filter(User.id.in_(query))
        # Delete the non activated accounts only if it is asked to.
        if delete:
            for user in qry.all():
                DBSession.delete(user)
        # If the non activated accounts are not asked to be deleted,
        # return their details.
        else:
            return qry.all()

    @staticmethod
    def get_list(active=None, order=None, limit=None):
        """Get a list of all of the user accounts"""
        user_query = User.query.order_by(User.username)

        if active is not None:
            user_query = user_query.filter(User.activated == active)

        if order:
            user_query = user_query.order_by(getattr(User, order))
        else:
            user_query = user_query.order_by(User.signup)

        if limit:
            user_query = user_query.limit(limit)

        return user_query.all()

    @staticmethod
    def get(user_id=None, username=None, email=None, api_key=None):
        """Get the user instance for this information

        :param user_id: integer id of the user in db
        :param username: string user's name
        :param inactive: default to only get activated true

        """
        user_query = User.query

        if username is not None:
            return user_query.filter(User.username == username).first()

        if user_id is not None:
            return user_query.filter(User.id == user_id).first()

        if email is not None:
            return user_query.filter(User.email == email).first()

        if api_key is not None:
            return user_query.filter(User.api_key == api_key).first()

        return None

    @staticmethod
    def auth_groupfinder(userid, request):
        """Pyramid wants to know what groups a user is in

        We need to pull this from the User object that we've stashed in the
        request object

        """
        user = request.user
        if user is not None:
            if user.is_admin:
                return 'admin'
            else:
                return 'user'
        return None

    @staticmethod
    def acceptable_password(password):
        """Verify that the password is acceptable

        Basically not empty, has more than 3 chars...

        """
        LOG.debug("PASS")
        LOG.debug(password)

        if password is not None:
            LOG.debug(len(password))

        if password is None:
            return False

        if len(password) < 3:
            return False

        return True

    @staticmethod
    def signup_user(email, signup_method):
        # Get this invite party started, create a new user acct.
        new_user = User()
        new_user.email = email.lower()
        new_user.username = email.lower()
        new_user.invited_by = signup_method
        new_user.api_key = User.gen_api_key()

        # they need to be deactivated
        new_user.reactivate(u'invite')

        # decrement the invite counter
        DBSession.add(new_user)
        return new_user


class User(Base):
    """Basic User def"""
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(255), unique=True)
    name = Column(Unicode(255))
    _password = Column('password', Unicode(60))
    email = Column(Unicode(255), unique=True)
    activated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    signup = Column(DateTime, default=datetime.utcnow)
    api_key = Column(Unicode(12))
    invite_ct = Column(Integer, default=0)
    invited_by = Column('invited_by', Unicode(255))
    BaseConnection = relation(BaseConnection,
                              backref="users")

    activation = relation(
        Activation,
        cascade="all, delete, delete-orphan",
        uselist=False,
        backref='user')

    def __init__(self):
        """By default a user starts out deactivated"""
        self.activation = Activation(u'signup')
        self.activated = False

    def _set_password(self, password):
        """Hash password on the fly."""
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        # Hash a password for the first time, with a randomly-generated salt
        salt = bcrypt.gensalt(10)
        hashed_password = bcrypt.hashpw(password_8bit, salt)

        # Make sure the hased password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # fields
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the password hashed"""
        return self._password

    password = synonym('_password', descriptor=property(_get_password,
                                                        _set_password))

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.

        """
        # the password might be null as in the case of morpace employees
        # logging in via ldap. We check for that here and return them as an
        # incorrect login
        if self.password:
            salt = self.password[:29]
            return self.password == bcrypt.hashpw(password, salt)
        else:
            return False

    def safe_data(self):
        """Return safe data to be sharing around"""
        hide = ['_password', 'password', 'is_admin', 'api_key']
        return dict(
            [(k, v) for k, v in dict(self).iteritems() if k not in hide]
        )

    def deactivate(self):
        """In case we need to disable the login"""
        self.activated = False

    def reactivate(self, creator):
        """Put the account through the reactivation process

        This can come about via a signup or from forgotten password link

        """
        # if we reactivate then reinit this
        self.activation = Activation(creator)
        self.activated = False

    def has_invites(self):
        """Does the user have any invitations left"""
        return self.invite_ct > 0

    def invite(self, email):
        """Invite a user"""
        if not self.has_invites():
            return False
        if not email:
            raise ValueError('You must supply an email address to invite')
        else:
            # get this invite party started, create a new useracct
            new_user = UserMgr.signup_user(email, self.username)

            # decrement the invite counter
            self.invite_ct = self.invite_ct - 1
            DBSession.add(new_user)
            return new_user

    @staticmethod
    def gen_api_key():
        """Generate a 12 char api key for the user to use"""
        m = hashlib.sha256()
        m.update(get_random_word(12))
        return unicode(m.hexdigest()[:12])
