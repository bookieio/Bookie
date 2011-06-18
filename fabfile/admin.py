"""Fabric commands to help add new users to the system"""
from database import sample
from fabric.api import env
from fabric.api import require
from utils import parse_ini


def new_user(username, email):
    """Add new user function, pass username, email

    :param username: string of new user
    :param email: string of new email

    """
    require('hosts', provided_by=[sample])
    require('ini', provided_by=[sample])

    parse_ini(env["ini_file"])

    import transaction
    from bookie.models import initialize_sql
    from sqlalchemy import create_engine

    engine = create_engine(env.ini.get('app:bookie', 'sqlalchemy.url'))
    initialize_sql(engine)

    from bookie.models import DBSession
    from bookie.models.auth import get_random_word, User
    sess = DBSession()

    u = User()
    u.username = unicode(username)
    passwd = get_random_word(8)
    u.password = passwd
    u.email = unicode(email)
    u.activated = True
    u.is_admin = False
    u.api_key = User.gen_api_key()

    print dict(u)
    print passwd

    sess.add(u)
    sess.flush()
    transaction.commit()
