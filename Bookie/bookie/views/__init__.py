"""Basic views with no home"""
from pyramid.httpexceptions import HTTPFound


def my_view(request):
    """Iniital / view for now until we find a better one"""
    return HTTPFound(location=request.route_url("bmark_recent"))
