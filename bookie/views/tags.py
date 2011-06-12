"""Controllers related to viewing Tag information"""
import logging
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render
from pyramid.view import view_config

from bookie.lib import access
from bookie.models import BmarkMgr
from bookie.models import TagMgr

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


@view_config(route_name="tag_list", renderer="/tag/list.mako")
def tag_list(request):
    """Display a list of your tags"""
    tags_found = TagMgr.find()

    return {
        'tag_list': tags_found,
        'tag_count': len(tags_found),
    }


@view_config(route_name="tag_bmarks_ajax", renderer="morjson")
@view_config(route_name="tag_bmarks", renderer="/tag/bmarks_wrap.mako")
def bmark_list(request):
    """Display the list of bookmarks for this tag"""
    route_name = request.matched_route.name
    rdict = request.matchdict
    params = request.params

    # check if we have a page count submitted
    tags = rdict.get('tags')
    page = int(params.get('page', 0))

    # verify the tag exists before we go on
    # 404 if the tag isn't found
    exists = TagMgr.find(tags=tags)

    if not exists:
        raise HTTPNotFound()

    bmarks = BmarkMgr.find(tags=tags,
                           limit=RESULTS_MAX,
                           page=page,)

    if 'ajax' in route_name:
        html = render('bookie:templates/tag/bmarks.mako',
                      {
                         'tags': tags,
                         'bmark_list': bmarks,
                         'max_count': RESULTS_MAX,
                         'count': len(bmarks),
                         'page': page,
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
               }
