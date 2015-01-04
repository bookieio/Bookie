import logging

from pyramid.view import view_config

from bookie.lib.access import ReqAuthorize
from bookie.models.social import SocialMgr
from bookie.models.auth import UserMgr

LOG = logging.getLogger(__name__)


@view_config(route_name="user_account", renderer="/accounts/index.mako")
def account(request):
    """Index of account page

    You can only load your own account page. If you try to view someone else's
    you'll just end up with your own.

    """
    # if auth fails, it'll raise an HTTPForbidden exception
    with ReqAuthorize(request):
        user = UserMgr.get(username=request.user.username)
        connections = SocialMgr.get_all_connections(
            username=request.user.username).all()

        return {
            'user': user,
            'username': user.username,
            'connections': connections,
        }
