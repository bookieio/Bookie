from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from bookie.lib.access import RequestWithUserAttribute
from bookie.models import initialize_sql
from bookie.models.auth import UserMgr
from bookie.routes import build_routes

from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import ALL_PERMISSIONS


class RootFactory(object):
    __acl__ = [(Allow, Everyone, ALL_PERMISSIONS)]

    def __init__(self, request):
        if request.matchdict:
            self.__dict__.update(request.matchdict)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)

    authn_policy = AuthTktAuthenticationPolicy(
                       settings.get('auth.secret'),
                       callback=UserMgr.auth_groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                          root_factory='bookie.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.set_request_factory(RequestWithUserAttribute)

    config = build_routes(config)
    config.add_static_view('static', 'bookie:static')
    config.scan('bookie.views')

    return config.make_wsgi_app()
