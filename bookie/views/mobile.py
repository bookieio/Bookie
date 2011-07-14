import logging
from pyramid.view import view_config

from bookie.lib import access

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


@view_config(route_name="user_mobile", renderer="/mobile/index.mako")
def mobile_index(request):
    """Mobile index page

    The content is loaded via ajax calls so we just return the base html/js

    """

    with access.ReqAuthorize(request):
        # you have to be auth'd to get to the mobile right now
        return {'username': request.user.username, }
