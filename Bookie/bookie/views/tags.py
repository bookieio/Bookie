"""Controllers related to viewing Tag information"""
import logging
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPNotFound

from bookie.models import BmarkMgr
from bookie.models import TagMgr

LOG = logging.getLogger(__name__)
RESULTS_MAX = 50


def tag_list(request):
    """Display a list of your tags"""
    tag_list = TagMgr.find()

    return {
        'tag_list': tag_list,
        'tag_count': len(tag_list),
    }


def bmark_list(request):
    """Display the list of bookmarks for this tag"""
    rdict = request.matchdict

    # check if we have a page count submitted
    tag = rdict.get('tag')
    page = int(rdict.get('page', 0))

    # verify the tag exists before we go on
    # 404 if the tag isn't found
    exists = TagMgr.find(tags=[tag])

    if not exists:
        raise HTTPNotFound()

    bmarks = BmarkMgr.by_tag(tag,
                           limit=RESULTS_MAX,
                           page=page)

    return { 'tag': tag,
             'bmark_list': bmarks,
             'max_count': RESULTS_MAX,
             'count': len(bmarks),
             'page': page,
           }
