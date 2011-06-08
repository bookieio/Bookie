"""
Sample SQLAlchemy-powered model definition for the repoze.what SQL plugin.

This model definition has been taken from a quickstarted TurboGears 2 project,
but it's absolutely independent of TurboGears.

"""

import bcrypt
import logging
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Boolean
from sqlalchemy.orm import synonym

from bookie.models import Base

LOG = logging.getLogger(__name__)
GROUPS = ['admin', 'user']


class UserMgr(object):
    """ Wrapper for static/combined operations of User object"""

    @staticmethod
    def get_list():
        """Get a list of all of the user accounts"""
        return User.query.order_by(User.user_name).all()

    @staticmethod
    def get(user_id=None, user_name=None):
        """Get the user instance for this information

        :param user_id: integer id of the user in db
        :param user_name: string user's name

        """
        user_query = User.query

        if user_name is not None:
            return user_query.filter(User.user_name == user_name).first()

        if user_id is not None:
            return user_query.filter(User.user_id == user_id).first()

        return False


class User(Base):
    """Basic User def"""
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(255), unique=True)
    _password = Column('password', Unicode(60))
    email = Column(Unicode(255), unique=True)
    activated = Column(Boolean, default=0)
    is_admin = Column(Boolean, default=0)
    last_login = Column(DateTime, default=datetime.now)

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
