"""Controllers related to viewing Tag information"""
from bookie.models import BmarkMgr
from bookie.models import TagMgr


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

    bmarks = BmarkMgr.by_tag(tag,
                           limit=RESULTS_MAX,
                           page=page)

    return { 'tag': tag,
             'bmark_list': bmarks,
             'count': RESULTS_MAX,
             'page': page,
           }
