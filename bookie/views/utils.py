"""View callables for utilities like bookmark imports, etc"""
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.settings import asbool
from pyramid.view import view_config

from bookie.lib.importer import Importer
from bookie.lib.access import ReqAuthorize
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models.fulltext import get_fulltext_handler

LOG = logging.getLogger(__name__)


@view_config(route_name="user_import", renderer="/utils/import.mako")
def import_bmarks(request):
    """Allow users to upload a delicious bookmark export"""
    rdict = request.matchdict
    username = rdict.get('username')

    # if auth fails, it'll raise an HTTPForbidden exception
    with ReqAuthorize(request):
        data = {}
        post = request.POST
        if post:
            # we have some posted values
            files = post.get('import_file', None)

            if files is not None:
                # upload is there for use
                # process the file using the import script
                importer = Importer(files.file, username=username)

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


@view_config(route_name="search", renderer="/utils/search.mako")
@view_config(route_name="user_search", renderer="/utils/search.mako")
def search(request):
    """Display the search form to the user"""
    return {}


@view_config(route_name="search_results", renderer="/utils/results_wrap.mako")
@view_config(route_name="user_search_results", renderer="/utils/results_wrap.mako")
@view_config(route_name="api_bmark_search", renderer="morjson")
@view_config(route_name="user_api_bmark_search", renderer="morjson")
@view_config(route_name="search_results_rest", renderer="/utils/results_wrap.mako")
@view_config(route_name="user_search_results_rest", renderer="/utils/results_wrap.mako")
def search_results(request):
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

    mdict = request.matchdict
    rdict = request.GET

    if 'terms' in mdict:
        phrase = " ".join(mdict['terms'])
    else:
        phrase = rdict.get('search', '')

    username = rdict.get('username', None)

    # with content is always in the get string
    with_content = asbool(rdict.get('content', False))
    LOG.debug('with_content')
    LOG.debug(with_content)

    conn_str = request.registry.settings.get('sqlalchemy.url', False)
    searcher = get_fulltext_handler(conn_str)

    # check if we have a page count submitted
    params = request.params
    page = params.get('page', None)
    count = params.get('count', None)

    res_list = searcher.search(phrase, content=with_content, username=username)

    # we're going to fake this since we dont' have a good way to do this query
    # side
    if page is not None and count is not None:
        page = int(page)
        count = int(count)
        start = count * page
        end = start + count
        LOG.debug('counts')
        LOG.debug(start)
        LOG.debug(end)
        res_list = res_list[start:end]

    # if the route name is search_ajax we want a json response
    # else we just want to return the payload data to the mako template
    if 'ajax' in route_name or 'api' in route_name:
        return {
            'success': True,
            'message': "",
            'payload': {
                'search_results': [dict(res) for res in res_list],
                'result_count': len(res_list),
                'phrase': phrase,
                'page': page,
                'with_content': with_content,
            }
        }
    else:
        return {
            'search_results': res_list,
            'result_count': len(res_list),
            'phrase': phrase,
            'page': page,
            'with_content': with_content,
        }


@view_config(route_name="user_export", renderer="/utils/export.mako")
def export(request):
    """Handle exporting a user's bookmarks to file"""
    rdict = request.matchdict
    username = rdict.get('username')

    bmark_list = Bmark.query.join(Bmark.tags).filter(Bmark.username==username).all()
    request.response_content_type = 'text/html'

    headers = [('Content-Disposition', 'attachment; filename="bookie_export.html"')]
    setattr(request, 'response_headerlist', headers)

    return {
        'bmark_list': bmark_list,
    }


@view_config(route_name="redirect", renderer="/utils/redirect.mako")
@view_config(route_name="user_redirect", renderer="/utils/redirect.mako")
def redirect(request):
    """Handle redirecting to the selected url

    We want to increment the clicks counter on the bookmark url here

    """
    rdict = request.matchdict
    hash_id = rdict.get('hash_id', None)
    username = rdict.get('username', None)

    hashed = Hashed.query.get(hash_id)

    if not hashed:
        # for some reason bad link, 404
        return HTTPNotFound()

    hashed.clicks = hashed.clicks + 1

    if username is not None:
        bookmark = Bmark.query.\
                         filter(Bmark.hash_id==hash_id).\
                         filter(Bmark.username==username).one()
        bookmark.clicks = bookmark.clicks + 1

    return HTTPFound(location=hashed.url)
