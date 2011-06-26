"""
Handle application logging items

Current db model:

id, user, component, status, message, payload, tstamp

"""
import json
from bookie.models.applog import AppLogMgr


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
    component = "AUTH"

    @staticmethod
    def login(username, success, password=None):
        """Store that a user logged into the system"""
        get_status = lambda x: Log.INFO if x else Log.ERROR
        passwd = lambda x: None if password is None else {'password': password}

        status = get_status(success)
        message = "User {0} attempted to login {1}".format(username,
                                                          success)

        data = {
                'user': username,
                'component': AuthLog.component,
                'payload': passwd(password)
        }

        AuthLog.store(status, message, **data)


class BmarkLog(Log):
    """Bookmark specific log items"""
    component = "BMARKS"

    @staticmethod
    def export(for_user, current_user):
        """Note that a user has exported their bookmarks"""
        get_status = lambda x: Log.WARNING if x else Log.INFO

        your_export = False
        if current_user and current_user == for_user:
            your_export = True

        status = get_status(your_export)
        message = "User {0} exported the bookmarks for {1}".format(current_user,
                                                          for_user)

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
            kwargs['payload'] = json.dumps(dict(kwargs.get('payload')))

        AppLogMgr.store(**kwargs)
