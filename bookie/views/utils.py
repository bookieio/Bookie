"""View callables for utilities like bookmark imports, etc"""

import logging
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)
from pyramid.view import view_config
from sqlalchemy.orm import contains_eager

from bookie.lib.access import ReqAuthorize
from bookie.lib.applog import BmarkLog
from bookie.lib.importer import store_import_file

from bookie.bcelery import tasks
from bookie.models import (
    Bmark,
    DBSession,
    Hashed,
)
from bookie.models.fulltext import get_fulltext_handler
from bookie.models.queue import (
    NEW,
    ImportQueue,
    ImportQueueMgr,
)
from bookie.views import BookieView


LOG = logging.getLogger(__name__)


class ImportViews(BookieView):

    @view_config(route_name="user_import", renderer="/utils/import.mako")
    def import_bmarks(self):
        """Allow users to upload a bookmark export file for processing"""
        username = self.matchdict.get('username')

        # if auth fails, it'll raise an HTTPForbidden exception
        with ReqAuthorize(self.request):
            data = {}
            post = self.POST

            # We can't let them submit multiple times, check if this user has
            # an import in process.
            if ImportQueueMgr.get(username=username, status=NEW):
                # They have an import, get the information about it and shoot
                # to the template.
                return {
                    'existing': True,
                    'import_stats': ImportQueueMgr.get_details(
                        username=username)
                }

            if post:
                # we have some posted values
                files = post.get('import_file', None)

                if hasattr(files, 'filename'):
                    storage_dir_tpl = self.settings.get('import_files',
                                                        '/tmp/bookie')
                    storage_dir = storage_dir_tpl.format(
                        here=self.settings.get('app_root'))

                    out_fname = store_import_file(storage_dir, username, files)

                    # Mark the system that there's a pending import that needs
                    # to be completed
                    q = ImportQueue(username, unicode(out_fname))
                    DBSession.add(q)
                    DBSession.flush()
                    # Schedule a task to start this import job.
                    tasks.importer_process.delay(q.id)

                    return HTTPFound(
                        location=self.request.route_url('user_import',
                                                        username=username))
                else:
                    data['error'] = ["Please provide a file to import"]

                return data
            else:
                # we need to see if they've got
                # just display the form
                return {
                    'existing': False
                }

    @view_config(route_name="search", renderer="/utils/search.mako")
    @view_config(route_name="user_search", renderer="/utils/search.mako")
    def search(self):
        """Display the search form to the user"""
        # If this is a url /username/search then we need to update the search
        # form action to /username/results
        mdict = self.matchdict
        username = mdict.get('username', None)
        return {'username': username}

    @view_config(route_name="search_results",
                 renderer="/utils/results_wrap.mako")
    @view_config(route_name="user_search_results",
                 renderer="/utils/results_wrap.mako")
    @view_config(route_name="search_results_ajax", renderer="json")
    @view_config(route_name="user_search_results_ajax", renderer="json")
    @view_config(route_name="search_results_rest",
                 renderer="/utils/results_wrap.mako")
    @view_config(route_name="user_search_results_rest",
                 renderer="/utils/results_wrap.mako")
    def search_results(self):
        """Search for the query terms in the matchdict/GET params

        The ones in the matchdict win in the case that they both exist
        but we'll fall back to query string search=XXX

        """
        route_name = self.request.matched_route.name
        mdict = self.matchdict
        rdict = self.GET

        if 'terms' in mdict:
            phrase = " ".join(mdict['terms'])
        else:
            phrase = rdict.get('search', '')

        # Always search the fulltext content
        with_content = True

        conn_str = self.settings.get('sqlalchemy.url', False)
        searcher = get_fulltext_handler(conn_str)

        # check if we have a page count submitted
        params = self.params
        page = params.get('page', 0)
        count = params.get('count', 50)

        if rdict.get('search_mine') or 'username' in mdict:
            with_user = True
        else:
            with_user = False

        username = None
        if with_user:
            if 'username' in mdict:
                username = mdict.get('username')
            elif self.request.user and self.request.user.username:
                username = self.request.user.username

        res_list = searcher.search(
            phrase,
            content=with_content,
            username=username if with_user else None,
            ct=count,
            page=page,
        )

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
                    'username': username,
                }
            }
        else:
            return {
                'search_results': res_list,
                'count': len(res_list),
                'max_count': 50,
                'phrase': phrase,
                'page': page,
                'username': username,
            }

    @view_config(route_name="user_export", renderer="/utils/export.mako")
    def export(self):
        """Handle exporting a user's bookmarks to file"""
        mdict = self.matchdict
        username = mdict.get('username')

        if self.request.user is not None:
            current_user = self.request.user.username
        else:
            current_user = None

        bmark_list = Bmark.query.join(Bmark.tags).\
            options(
                contains_eager(Bmark.tags)
            ).\
            join(Bmark.hashed).\
            options(
                contains_eager(Bmark.hashed)
            ).\
            filter(Bmark.username == username).all()

        BmarkLog.export(username, current_user)

        self.request.response_content_type = 'text/html'

        headers = [('Content-Disposition',
                    'attachment; filename="bookie_export.html"')]
        setattr(self.request, 'response_headerlist', headers)

        return {
            'bmark_list': bmark_list,
        }

    @view_config(route_name="redirect", renderer="/utils/redirect.mako")
    @view_config(route_name="user_redirect", renderer="/utils/redirect.mako")
    def redirect(self):
        """Handle redirecting to the selected url

        We want to increment the clicks counter on the bookmark url here

        """
        mdict = self.matchdict
        hash_id = mdict.get('hash_id', None)
        username = mdict.get('username', None)

        hashed = Hashed.query.get(hash_id)

        if not hashed:
            # for some reason bad link, 404
            return HTTPNotFound()

        hashed.clicks = hashed.clicks + 1

        if username is not None:
            bookmark = Bmark.query.\
                filter(Bmark.hash_id == hash_id).\
                filter(Bmark.username == username).one()
            bookmark.clicks = bookmark.clicks + 1

        return HTTPFound(location=hashed.url)
