"""Basic views with no home"""
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name="home")
def home(request):
    """Inital / view for now until we find a better one"""
    return HTTPFound(location=request.route_url("bmark_recent"))
