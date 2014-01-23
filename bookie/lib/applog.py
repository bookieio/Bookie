"""
Handle application logging items

Current db model:

id, user, component, status, message, payload, tstamp

"""
import json
import logging
from bookie.models.applog import AppLogMgr

LOG = logging.getLogger(__name__)


class Log(object):
    """Log handler"""

    # status levels
    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3

    @staticmethod
    def store(status, message, **kwargs):
        """Store a log item"""
        LogRecord(status, message, **kwargs)


class AuthLog(Log):
    """Store auth specific log items"""
    component = u"AUTH"

    @staticmethod
    def login(username, success, password=None):
        """Store that a user logged into the system"""
        get_status = lambda x: Log.INFO if x else Log.ERROR
        passwd = lambda x: None if password is None else {'password': password}

        status = get_status(success)
        message = u"User {0} attempted to login {1}".format(username,
                                                            success)
        data = {
            'user': username,
            'component': AuthLog.component,
            'payload': passwd(password)
        }

        AuthLog.store(status, message, **data)

    @staticmethod
    def disabled(username):
        """Attempt to log into a disabled account"""
        msg = u"{0} is a disabled user account".format(username)

        data = {
            'user': username,
            'component': AuthLog.component
        }

        AuthLog.store(Log.INFO, msg, **data)

    @staticmethod
    def reactivate(username, success=True, code=None):
        """The account was marked for reactivation"""
        if success:
            msg = u"{0} was reactivated".format(username)
        else:
            msg = u"{0} attempted to reactivate with invalid credentials"
            msg = msg.format(username)

        LOG.debug(msg)
        data = {
            'user': username,
            'component': AuthLog.component,
            'payload': {
                'success': success,
                'code': code,
            }
        }

        AuthLog.store(Log.INFO, msg, **data)


class BmarkLog(Log):
    """Bookmark specific log items"""
    component = u"BMARKS"

    @staticmethod
    def export(for_user, current_user):
        """Note that a user has exported their bookmarks"""
        get_status = lambda x: Log.WARNING if x else Log.INFO

        your_export = False
        if current_user and current_user == for_user:
            your_export = True

        elif current_user is None:
            current_user = "None"

        status = get_status(your_export)
        message = u"User {0} exported the bookmarks for {1}".format(
            current_user, for_user)

        data = {
            'user': current_user,
            'component': BmarkLog.component,
        }

        BmarkLog.store(status, message, **data)


class LogRecord(object):
    """A record in the log"""

    def __init__(self, status, message, **kwargs):
        """A record in the log"""
        kwargs['status'] = status
        kwargs['message'] = message

        # we need to hash down the payload if there is one
        if 'payload' in kwargs and kwargs['payload'] is not None:
            kwargs['payload'] = unicode(
                json.dumps(dict(kwargs.get('payload')))
            )

        AppLogMgr.store(**kwargs)


class SignupLog(object):
    """Signup Log records."""

    def __init__(self, status, message, **kwargs):
        """A record in the log"""
        kwargs['status'] = status
        kwargs['message'] = message

        # we need to hash down the payload if there is one
        if 'payload' in kwargs and kwargs['payload'] is not None:
            kwargs['payload'] = json.dumps(dict(kwargs.get('payload')))

        AppLogMgr.store(**kwargs)
