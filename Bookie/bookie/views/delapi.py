"""Pyramid controller for the delicious api compatible url calls

"""
import logging
from cgi import escape
from datetime import datetime
from bookie.lib.access import Authorize
from bookie.models import DBSession, NoResultFound
from bookie.models import BmarkMgr
from bookie.models import Bmark
from bookie.models import Hashed
from pyramid.httpexceptions import HTTPNotFound

from bookie.models.fulltext import get_fulltext_handler

LOG = logging.getLogger(__name__)


def posts_add(request):
    """Add a new bmark into the system given request params

    For example usage make sure to check out the unit tests in the
    test_delicious directory

    """
    params = request.GET

    with Authorize(request.registry.settings.get('api_key', ''),
                   params.get('api_key', None)):

        request.response_content_type = 'text/xml'
        if 'url' in params and params['url']:
            # check if we already have this
            try:
                mark = BmarkMgr.get_by_url(params['url'])

                mark.description = params.get('description', mark.description)
                mark.extended = params.get('extended', mark.extended)

                new_tags = params.get('tags', None)
                if new_tags:
                    mark.update_tags(new_tags)

            except NoResultFound:
                # then let's store this thing

                # if we have a dt param then set the date to be that manual
                # date
                if 'dt' in request.params:
                    # date format by delapi specs:
                    # CCYY-MM-DDThh:mm:ssZ
                    fmt = "%Y-%m-%dT%H:%M:%SZ"
                    stored_time = datetime.strptime(request.params['dt'], fmt)
                else:
                    stored_time = None

                # we want to store fulltext info so send that along to the
                # import processor
                conn_str = request.registry.settings.get('sqlalchemy.url',
                                                         False)
                fulltext = get_fulltext_handler(conn_str)

                BmarkMgr.store(params['url'],
                             params.get('description', ''),
                             params.get('extended', ''),
                             params.get('tags', ''),
                             dt=stored_time,
                             fulltext=fulltext,
                       )

            return '<result code="done" />'
        else:
            return '<result code="Bad Request: missing url" />'


def posts_delete(request):
    """Remove a bmark from the system"""
    params = request.GET
    request.response_content_type = 'text/xml'

    with Authorize(request.registry.settings.get('api_key', ''),
                   params.get('api_key', None)):
        if 'url' in params and params['url']:
            try:
                bmark = BmarkMgr.get_by_url(params['url'])

                session = DBSession()
                session.delete(bmark)

                return '<result code="done" />'

            except NoResultFound:
                # if it's not found, then there's not a bookmark to delete
                return '<result code="Bad Request: bookmark not found" />'


def posts_get(request):
    """Return one or more bmarks based on search criteria

    Supported criteria:
    - url

    TBI:
    - tag={TAG}+{TAG}+
    - dt={CCYY-MM-DDThh:mm:ssZ}
    - hashes={MD5}+{MD5}+...+{MD5}

    """
    params = request.GET
    request.response_content_type = 'text/xml'
    try:
        if 'url' in params and params['url']:
            url = request.GET['url']
            bmark = BmarkMgr.get_by_url(url=url)

            if not bmark:
                return HTTPNotFound()

            # we need to escape any html entities in things
            return {'datefound': bmark.stored.strftime('%Y-%m-%d'),
                    'posts': [bmark],
                    'escape': escape, }
        else:
            request.override_renderer = 'string'
            return '<result code="Not Found" />'

    except NoResultFound:
        request.override_renderer = 'string'
        return '<result code="Not Found" />'
