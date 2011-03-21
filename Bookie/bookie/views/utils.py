"""View callables for utilities like bookmark imports, etc"""
import logging
from pyramid.httpexceptions import HTTPFound

from bookie.lib.importer import Importer
from bookie.lib.access import Authorize
from bookie.models import Bmark
from bookie.models.fulltext import get_fulltext_handler

LOG = logging.getLogger(__name__)


def import_bmarks(request):
    """Allow users to upload a delicious bookmark export"""
    data = {}
    post = request.POST
    LOG.error(request.registry.settings.get('api_key', ''))
    LOG.error(post.get('api_key'))
    if post:
        # we have some posted values
        with Authorize(request.registry.settings.get('api_key', ''),
                       post.get('api_key', None)):

            # if auth fails, it'll raise an HTTPForbidden exception
            files = post.get('import_file', None)

            if files is not None:
                # upload is there for use
                # process the file using the import script
                importer = Importer(files.file)

                # we want to store fulltext info so send that along to the
                # import processor
                conn_str = request.registry.settings.get('sqlalchemy.url',
                                                         False)
                searcher = get_fulltext_handler(conn_str)
                importer.process(fulltext=searcher)

                # @todo get a count of the imported bookmarks and setup a flash
                # message. Forward to / and display the import message

                # request.session.flash("Error something")
                return HTTPFound(location=request.route_url('home'))
            else:
                msg = request.session.pop_flash()

                if msg:
                    data['error'] = msg
                else:
                    data['error'] = None

            return data
    else:
        # just display the form
        return {}


def search(request):
    """Search for the content in the matchdict"""
    rdict = request.GET

    # check if we have a page count submitted
    phrase = rdict.get('search', '')

    conn_str = request.registry.settings.get('sqlalchemy.url', False)
    searcher = get_fulltext_handler(conn_str)

    res = searcher.search(phrase)
    res_list = (mark.bmark for mark in res)

    return {
        'search_results': res_list,
        'result_count': len(res),
        'phrase': phrase,
    }


def export(request):
    """Handle exporting a user's bookmarks to file"""
    bmark_list = Bmark.query.join(Bmark.tags).all()
    return {
        'bmark_list': bmark_list,
    }
