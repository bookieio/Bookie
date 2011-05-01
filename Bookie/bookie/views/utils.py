"""View callables for utilities like bookmark imports, etc"""
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render
from pyramid.settings import asbool

from bookie.lib.importer import Importer
from bookie.lib.access import Authorize
from bookie.models import Bmark
from bookie.models import Hashed
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
    """Search for the query terms in the matchdict/GET params

    The ones in the matchdict win in the case that they both exist
    but we'll fall back to query string search=XXX

    with_content
        is always GET and specifies if we're searching the fulltext of pages

    Ajax Requests:
        We also use this method to serve ajax requests
        If we have _ajax in the name of the route it's an ajax match
        Make sure we sent out the proper MorJSON response

    """
    route_name = request.matched_route.name

    LOG.debug(request.headers)

    mdict = request.matchdict
    rdict = request.GET

    if 'terms' in mdict:
        phrase = " ".join(mdict['terms'])
    else:
        phrase = rdict.get('search', '')

    # with content is always in the get string
    with_content = asbool(rdict.get('content', False))

    conn_str = request.registry.settings.get('sqlalchemy.url', False)
    searcher = get_fulltext_handler(conn_str)

    res_list = searcher.search(phrase, content=with_content)

    # if the route name is search_ajax we want a json response
    # else we just want to return the payload data to the mako template
    if 'ajax' in route_name:
        html = render('bookie:templates/utils/results.mako',
                    { 'search_results': res_list,
                      'result_count': len(res_list),
                      'phrase': phrase.replace(" ", " OR "),
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
        return {
            'search_results': res_list,
            'result_count': len(res_list),
            'phrase': phrase.replace(" ", " OR "),
        }


def export(request):
    """Handle exporting a user's bookmarks to file"""
    bmark_list = Bmark.query.join(Bmark.tags).all()
    request.response_content_type = 'text/html'
    headers = [('Content-Disposition', 'attachment; filename="bookie_export.html"')]
    setattr(request, 'response_headerlist', headers)

    return {
        'bmark_list': bmark_list,
    }

def redirect(request):
    """Handle redirecting to the selected url

    We want to increment the clicks counter on the bookmark url here

    """
    rdict = request.matchdict
    hash_id = rdict.get('hash_id', None)

    hashed = Hashed.query.get(hash_id)
    hashed.clicks = hashed.clicks + 1

    if not hashed:
        # for some reason bad link, 404
        return HTTPNotFound()

    return HTTPFound(location=hashed.url)


