"""Pyramid controller for the delicious api compatible url calls

"""
import logging
from cgi import escape
from datetime import datetime
from StringIO import StringIO

from pyramid.view import view_config

from bookie.lib.access import ApiAuthorize
from bookie.lib.readable import ReadContent
from bookie.models import DBSession, NoResultFound
from bookie.models import BmarkMgr
from bookie.models import Readable
from bookie.models import TagMgr
from pyramid.httpexceptions import HTTPNotFound

from bookie.models.fulltext import get_fulltext_handler

LOG = logging.getLogger(__name__)


@view_config(route_name="del_post_add", renderer="string")
def posts_add(request):
    """Add a new bmark into the system given request params

    For example usage make sure to check out the unit tests in the
    test_delicious directory

    """
    params = request.params

    with ApiAuthorize(request.registry.settings.get('api_key', ''),
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

                mark = BmarkMgr.store(params['url'],
                             params.get('description', ''),
                             params.get('extended', ''),
                             params.get('tags', ''),
                             dt=stored_time,
                             fulltext=fulltext,
                       )

            # if we have content, stick it on the object here
            if 'content' in request.params:
                content = StringIO(request.params['content'])
                content.seek(0)
                parsed = ReadContent.parse(content, content_type="text/html")

                mark.hashed.readable = Readable()
                mark.hashed.readable.content = parsed.content
                mark.hashed.readable.content_type = parsed.content_type
                mark.hashed.readable.status_code = parsed.status
                mark.hashed.readable.status_message = parsed.status_message

            return '<result code="done" />'
        else:
            return '<result code="Bad Request: missing url" />'


@view_config(route_name="del_post_delete", renderer="string")
def posts_delete(request):
    """Remove a bmark from the system"""
    params = request.params
    request.response_content_type = 'text/xml'

    with ApiAuthorize(request.registry.settings.get('api_key', ''),
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


@view_config(route_name="del_post_get", renderer="/delapi/posts_get.mako")
def posts_get(request):
    """Return one or more bmarks based on search criteria

    Supported criteria:
    - url

    TBI:
    - tag={TAG}+{TAG}+
    - dt={CCYY-MM-DDThh:mm:ssZ}
    - hashes={MD5}+{MD5}+...+{MD5}

    """
    params = request.params
    request.response_content_type = 'text/xml'
    LOG.debug(params)
    try:
        if 'url' in params and params['url']:
            url = request.params['url']
            LOG.debug(url)
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


@view_config(route_name="del_tag_complete", renderer="/delapi/tags_complete.mako")
def tags_complete(request):
    """Complete a tag based on the given text

    :@param tag: GET string, tag=sqlalchemy
    :@param current: GET string of tags we already have python+database

    """
    params = request.GET
    request.response_content_type = 'text/xml'

    if 'current' in params and params['current'] != "":
        current_tags = params['current'].split()
    else:
        current_tags = None

    LOG.debug('current_tags')
    LOG.debug(current_tags)

    if 'tag' in params and params['tag']:
        tag = params['tag']
        tags = TagMgr.complete(tag, current=current_tags)

        # we need to escape any html entities in things
        return { 'tags': tags }
