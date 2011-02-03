import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from bookie_app.lib.base import BaseController, render
from bookie_app.model import meta
from bookie_app.model.bookmarks import Bookmark
from bookie_app.model.tags import TagManager

log = logging.getLogger(__name__)

class D1Controller(BaseController):

    def posts_add(self):
        """ Delicious API for posts/add

        :param url: (required) the url of the item.
        :param description: (required) the description of the item.
        :param extended: (optional) notes for the item.
        :param tags:  (optional) tags for the item (space delimited).
        :param dt: CCYY-MM-DDThh:mm:ssZ (optional) datestamp of the item
        :param replace: (optional) don't replace post if given url has already been posted.
        :param shared: no (optional) make the item private

        """

        log.debug(request.params)
        bmark = Bookmark(request.params['url'])
        tag_list = TagManager.parse(request.params['tags'], store=True)

        bmark.tags = tag_list
        meta.Session.add(bmark)
        meta.Session.commit()

        return '<result code="done" />'
