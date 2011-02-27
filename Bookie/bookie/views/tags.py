from bookie.models import DBSession
from bookie.models import NoResultFound
from bookie.models import BmarkMgr
from bookie.models import Tag
from bookie.models import TagMgr

from pyramid.httpexceptions import HTTPNotFound

RESULTS_MAX = 50


def list(request):
    """Display a list of your tags"""
    tag_list = TagMgr.find()

    return {
        'tag_list': tag_list,
        'tag_count': len(tag_list),
        'route_url': request.route_url,
    }


def bmark_list(request):
    """Display the list of bookmarks for this tag"""
    rdict = request.matchdict

    # check if we have a page count submitted
    tag = rdict.get('tag')
    page = int(rdict.get('page', 0))

    bmark_list = BmarkMgr.by_tag(tag,
                           limit=RESULTS_MAX,
                           page=page)

    return { 'tag': tag,
             'bmark_list': bmark_list,
             'count': RESULTS_MAX,
             'page': page,
             'route_url': request.route_url,
           }
