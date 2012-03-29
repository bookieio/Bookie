"""Basic views with no home"""
import logging
from pyramid.view import view_config


LOG = logging.getLogger(__name__)


@view_config(
    route_name="dashboard",
    renderer="/stats/dashboard.mako")
def dashboard(request):
    """A public dashboard of the system
    """
    return {}
