#!/usr/bin/env python
"""Handle user management tasks from the cmd line for this Bookie instance

    usrmgr.py --add rharding --email rharding@mitechie.com

"""
import argparse

from ConfigParser import ConfigParser
from os import path
from bookie.models import initialize_sql
from bookie.models.auth import get_random_word
from bookie.models.auth import User
from bookie.models.auth import UserMgr

def parse_args():
    """Handle arguments building and processing"""
    desc = "Update existing bookbmarks with the readability parsed"

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--list', '-l',
        dest='getlist',
        action='store_true',
        default=None,
        help='Get the list of users from the system.')

    parser.add_argument('--ini',
        dest='ini',
        action='store',
        default='bookie.ini',
        help='The .ini configuration file to use for getting db access')

    parser.add_argument('--new', '-n',
        dest="newuser",
        action='store_true',
        default=None,
        help='Add new user to the system')

    parser.add_argument('--username', '-u',
        dest='username',
        action='store',
        default=None,
        help='The username to use for this task.')

    parser.add_argument('--email', '-e',
        dest='email',
        action='store',
        default=None,
        help='The email to use for this task.')

    parser.add_argument('--reset-password', '-r',
        dest="reset",
        action='store_true',
        default=None,
        help="Reset the user's password")

    parser.add_argument('--password', '-p',
        dest='password',
        action='store',
        default=None,
        help='The password to use for this task.')

    args = parser.parse_args()
    return args

def _init_sql(args):
    """Init the sql session for things to work out"""
    ini = ConfigParser()
    ini_path = path.join(path.dirname(path.dirname(path.dirname(__file__))), args.ini)
    ini.readfp(open(ini_path))
    here = path.abspath(path.join(path.dirname(__file__), '../../'))
    ini.set('app:main', 'here', here)
    initialize_sql(dict(ini.items("app:main")))


def _get_userlist(args):
    """Fetch a list of users from the system and output to stdout"""
    _init_sql(args)

    for user in UserMgr.get_list():
        print("{0:<10} {1:<20} {2:<50}".format(
            user.username,
            user.name,
            user.email))


def _new_user(args):
    """Handle adding a new user to the system.

    If you don't include the required info, it will prompt you for it

    """
    if not args.username:
        args.username = raw_input('username? ')

    if not args.email:
        args.email = raw_input('email address? ')

    if not args.username or not args.email:
        raise Exception('Must supply a username and email address')

    import transaction
    _init_sql(args)
    from bookie.models import DBSession
    sess = DBSession()

    u = User()
    u.username = unicode(args.username)
    passwd = get_random_word(8)
    u.password = passwd
    u.email = unicode(args.email)
    u.activated = True
    u.is_admin = False
    u.api_key = User.gen_api_key()

    print dict(u)
    print passwd

    sess.add(u)
    sess.flush()
    transaction.commit()


def _reset_password(args):
    """Reset a user's password"""

    if not args.username:
        args.username = raw_input('username? ')

    if not args.password:
        args.password = raw_input('password? ')

    if not args.username or not args.password:
        raise Exception('Must supply a username and password')

    import transaction
    _init_sql(args)
    from bookie.models import DBSession
    sess = DBSession()

    u = UserMgr.get(username=unicode(args.username))
    u.password = args.password
    sess.flush()
    transaction.commit()


def dispatch(args):
    """Based on the args, build our task up and complete it for the user"""

    if args.getlist:
        return _get_userlist(args)

    if args.newuser:
        return _new_user(args)

    if args.reset:
        return _reset_password(args)

if __name__ == '__main__':
    args = parse_args()
    dispatch(args)
