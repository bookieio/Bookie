"""Handle user management tasks from the cmd line for this Bookie instance

    usrmgr.py --add rharding --email rharding@mitechie.com

"""
import sys
import argparse
from ConfigParser import ConfigParser
from os import path

from prettytable import PrettyTable

from bookie.models import initialize_sql
from bookie.models.auth import get_random_word
from bookie.models.auth import User
from bookie.models.auth import UserMgr


def _init_sql(args):
    """Init the sql session for things to work out"""
    ini = ConfigParser()
    ini_path = path.join(path.dirname(path.dirname(path.dirname(__file__))),
                         args.ini)
    ini.readfp(open(ini_path))
    here = path.abspath(path.join(path.dirname(__file__), '../../'))
    ini.set('app:main', 'here', here)
    initialize_sql(dict(ini.items("app:main")))


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.exit(2)


def main():
    parser = ArgumentParser(
        epilog='use "bookie-manage command --help" to see command parameters'
    )

    subparser = parser.add_subparsers(title='basic commands', metavar='')

    parser.add_argument(
        '--ini',
        dest='ini',
        action='store',
        default='bookie.ini',
        help='The .ini configuration file to use for getting db access, default is "bookie.ini"'
    )
    parser_list_user = subparser.add_parser(
        'list-user', help='Get the list of users'
    )
    parser_list_user.set_defaults(func=list_user_cmd)

    parser_new_user = subparser.add_parser(
        'new-user', help='Adding new user'
    )
    parser_new_user.add_argument(
        '--username', '-u',
        dest='username',
        action='store',
        default=None
    )
    parser_new_user.add_argument(
        '--email', '-e',
        dest='email',
        action='store',
        default=None
    )
    parser_new_user.add_argument(
        '--password', '-p',
        dest='password',
        action='store',
        default=None
    )
    parser_new_user.set_defaults(func=new_user_cmd)

    parser_reset_password = subparser.add_parser(
        'reset-password', help='Reset user password'
    )
    parser_reset_password.add_argument(
        '--username', '-u',
        dest='username',
        action='store',
        default=None
    )
    parser_reset_password.add_argument(
        '--password', '-p',
        dest='password',
        action='store',
        default=None
    )
    parser_reset_password.set_defaults(func=reset_password_cmd)

    args = parser.parse_args()
    args.func(args)


def list_user_cmd(args):
    """Fetch a list of users from the system and output to stdout"""
    _init_sql(args)

    t = PrettyTable(['username', 'name', 'email'])
    t.align = 'l'

    for user in UserMgr.get_list():
        t.add_row([user.username, user.name, user.email])

    print(t)


def new_user_cmd(args):
    """Handle adding a new user to the system.

    If you don't include the required info, it will prompt you for it
    """
    if not args.username:
        args.username = raw_input('username ? ')

    if not args.email:
        args.email = raw_input('email address ? ')

    if not args.username or not args.email:
        raise Exception('Must supply a username and email address')

    if not args.password:
        args.password = get_random_word(8)

    import transaction
    _init_sql(args)
    from bookie.models import DBSession
    sess = DBSession()

    u = User()
    u.username = unicode(args.username)
    u.password = args.password
    u.email = unicode(args.email)
    u.activated = True
    u.is_admin = False
    u.api_key = User.gen_api_key()

    print("""New user created :
    username : %s
    email : %s
    password : %s""" % (
        u.username,
        u.email,
        args.password
    ))

    sess.add(u)
    sess.flush()
    transaction.commit()


def reset_password_cmd(args):
    """Reset a user's password"""

    if not args.username:
        args.username = raw_input('username ? ')

    if not args.password:
        args.password = raw_input('password ? ')

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
    print("Password updated")
