"""Controllers related to viewing Tag information"""
import logging
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render

from bookie.lib import access
from bookie.models import BmarkMgr
from bookie.models import TagMgr

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


def tag_list(request):
    """Display a list of your tags"""
    tags_found = TagMgr.find()

    return {
        'tag_list': tags_found,
        'tag_count': len(tags_found),
    }


def bmark_list(request):
    """Display the list of bookmarks for this tag"""
    route_name = request.matched_route.name
    rdict = request.matchdict

    # check if we have a page count submitted
    tags = rdict.get('tags')
    page = int(rdict.get('page', 0))

    # verify the tag exists before we go on
    # 404 if the tag isn't found
    exists = TagMgr.find(tags=tags)

    if not exists:
        raise HTTPNotFound()

    bmarks = BmarkMgr.by_tag(tags,
                           limit=RESULTS_MAX,
                           page=page)

    if 'ajax' in route_name:
        html = render('bookie:templates/tag/bmarks.mako',
                      {
                         'tags': tags,
                         'bmark_list': bmarks,
                         'max_count': RESULTS_MAX,
                         'count': len(bmarks),
                         'page': page,
                         'allow_edit': access.edit_enabled(request.registry.settings),
                       },
                  request=request)
        return {
            'success': True,
            'message': "",
            'payload': {
                'html': html,
            }
        }

    else:
        return {'tags': tags,
                 'bmark_list': bmarks,
                 'max_count': RESULTS_MAX,
                 'count': len(bmarks),
                 'page': page,
                 'allow_edit': access.edit_enabled(request.registry.settings),
               }
