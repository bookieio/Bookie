import logging
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render
from pyramid.view import view_config

from bookie.lib import access
from bookie.models import BmarkMgr
from bookie.models import TagMgr

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


@view_config(route_name="mobile", renderer="/mobile/index.mako")
def mobile_index(request):
    """Mobile index page"""
    # tags_found = TagMgr.find()

    return {
        'test': 'Testing'
        # 'tag_list': tags_found,
        # 'tag_count': len(tags_found),
    }
