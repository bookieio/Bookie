"""
Sample SQLAlchemy-powered model definition for the repoze.what SQL plugin.

This model definition has been taken from a quickstarted TurboGears 2 project,
but it's absolutely independent of TurboGears.

"""

import bcrypt
import hashlib
import logging
import random

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Boolean
from sqlalchemy.orm import synonym

from bookie.models import Base

LOG = logging.getLogger(__name__)
GROUPS = ['admin', 'user']


def get_random_word(wordLen):
    word = ''
    for i in xrange(wordLen):
        word += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/&=')
    return word


class UserMgr(object):
    """ Wrapper for static/combined operations of User object"""

    @staticmethod
    def get_list(ignore_activated=False):
        """Get a list of all of the user accounts"""
        user_query = User.query.order_by(User.username)

        if not ignore_activated:
            user_query = user_query.filter(User.activated == True)

        return user_query.all()

    @staticmethod
    def get(user_id=None, username=None):
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

        return None

    @staticmethod
    def auth_groupfinder(userid, request):
        """Pyramid wants to know what groups a user is in

        We need to pull this from the User object that we've stashed in the request
        object

        """
        LOG.debug('GROUP FINDER')
        LOG.debug(userid)
        LOG.debug(request)
        user = request.user
        LOG.debug(user)
        if user is not None:
            if user.is_admin:
                return 'admin'
            else:
                return 'user'
        return None


class User(Base):
    """Basic User def"""
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(255), unique=True)
    _password = Column('password', Unicode(60))
    email = Column(Unicode(255), unique=True)
    activated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    api_key = Column(Unicode(12))

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
        # the password might be null as in the case of morpace employees logging
        # in via ldap. We check for that here and return them as an incorrect
        # login
        if self.password:
            salt = self.password[:29]
            return self.password == bcrypt.hashpw(password, salt)
        else:
            return False

    def deactivate(self):
        """In case we need to disable the login"""
        self.activated = False

    @staticmethod
    def gen_api_key():
        """Generate a 12 char api key for the user to use"""
        m = hashlib.sha256()
        m.update(get_random_word(12))
        return unicode(m.hexdigest()[:12])
