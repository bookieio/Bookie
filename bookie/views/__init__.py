"""Basic views with no home"""
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from bookie.models.auth import UserMgr


class BookieView(object):

    def _helpers(self):
        self.matchdict = self.request.matchdict
        self.GET = self.request.GET
        self.POST = self.request.POST
        self.params = self.request.params
        self.settings = self.request.registry.settings

    def __init__(self, request):
        self.request = request
        self._helpers()


@view_config(route_name="home", renderer="index.mako")
@view_config(route_name="user_home", renderer="index.mako")
def home(request):
    """Inital / view for now until we find a better one"""
    rdict = request.matchdict
    username = rdict.get('username', None)
    if username:
        username = username.lower()

    if not request.user:
        return {}
    else:
        if not username:
            return HTTPFound(location=request.route_url("bmark_recent"))
        else:
            # we need to see if we have a user by this name
            user = UserMgr.get(username=username)

            if not user:
                return HTTPNotFound()
            else:
                return HTTPFound(
                    location=request.route_url("user_bmark_recent",
                                               username=username))
