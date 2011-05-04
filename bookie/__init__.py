from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from bookie.models import initialize_sql
from bookie.routes import build_routes


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)

    unencrypt = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    config = Configurator(settings=settings, session_factory=unencrypt)
    config = build_routes(config)
    config.add_static_view('static', 'bookie:static')
    config.scan('bookie.views')

    return config.make_wsgi_app()
