"""Test the fulltext implementation"""
import logging
import os
import transaction
import urllib

from nose.tools import ok_
from pyramid import testing
from unittest import TestCase

from bookie.lib.readable import ReadContent
from bookie.lib.readable import ReadUrl

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Tag
from bookie.models import bmarks_tags
from bookie.models.fulltext import get_fulltext_handler
from bookie.models.fulltext import SqliteFulltext


LOG = logging.getLogger(__file__)


class TestReadable(TestCase):
    """Test that our fulltext classes function"""

    def test_url_content(self):
        """Test that we set the correct status"""

        url = 'http://lococast.net/archives/475'
        read = ReadUrl.parse(url)

        ok_(read.status == 200, "The status is 200" + str(read.status))
        ok_(not read.is_image(), "The content is not an image")
        ok_(read.content is not None, "Content should not be none")
        ok_('Lococast' in read.content,
                "The word Lococast is in the content: " + str(read.content))

    def test_404_url(self):
        """Test that we get the proper errors in a missing url"""
        url = 'http://lococast.net/archives/001'
        read = ReadUrl.parse(url)

        ok_(read.status == 404, "The status is 404: " + str(read.status))
        ok_(not read.is_image(), "The content is not an image")
        ok_(read.content is None, "Content should be none")

    def test_given_content(self):
        """Test that we can parse out given html content ahead of time"""

        file_path = os.path.dirname(__file__)
        html_content = open(os.path.join(file_path, 'readable_sample.html'))

        read = ReadContent.parse(html_content)

        ok_(read.status == 1, "The status is 1: " + str(read.status))
        ok_(not read.is_image(), "The content is not an image")
        ok_(read.content is not None, "Content should not be none")
        ok_('Bookie' in read.content,
                u"The word Bookie is in the content: " + unicode(read.content))

    def test_non_net_url(self):
        """I might be bookmarking something internal bookie can't access"""
        test_url = "http://r2"
        read = ReadUrl.parse(test_url)

        ok_(read.status == 901, "The status is 901: " + str(read.status))
        ok_(not read.is_image(), "The content is not an image")
        ok_(read.content is None, "Content should be none: " + str(read.content))

    def test_image_url(self):
        """Verify we don't store, but just tag an image url"""
        img_url = 'http://www.ndftz.com/nickelanddime.png'
        read = ReadUrl.parse(img_url)

        ok_(read.status == 200, "The status is 200: " + str(read.status))
        ok_(read.content is None, "Content should be none: ")

    def test_nonworking_url(self):
        """Testing some urls we know we had issues with initially"""
        urls = { 'CouchSurfing': 'http://allthatiswrong.wordpress.com/2010/01/24/a-criticism-of-couchsurfing-and-review-of-alternatives/#problems',
                 'Bewelcome': 'http://bewelcome.info',
                 'Electronic': 'https://www.fbo.gov/index?s=opportunity&mode=form&tab=core&id=dd11f27254c796f80f2aadcbe4158407',
        }

        for key, url in urls.iteritems():
            LOG.debug(url)
            read = ReadUrl.parse(url)

            ok_(read.status == 200, "The status is 200: " + str(read.status))
            ok_(read.content is not None, "Content should not be none: ")

class TestReadableFulltext(TestCase):
    """Test that our fulltext index function"""

    def setUp(self):
        """Setup Tests"""
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """Tear down each test"""
        testing.tearDown()
        session = DBSession()
        Bmark.query.delete()
        Tag.query.delete()
        Hashed.query.delete()
        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()

    def _get_good_request(self):
        """Return the basics for a good add bookmark request"""
        session = DBSession()
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'api_key': u'testapi',
                'content': 'bmark content is the best kind of content man',
        }

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/delapi/posts/add?' + req_params)
        session.flush()
        transaction.commit()
        return res

    def test_get_handler(self):
        """Verify we get the right type of full text store object"""
        sqlite_str = "sqlite:///somedb.db"

        handler = get_fulltext_handler(sqlite_str)

        ok_(isinstance(handler, SqliteFulltext),
                "Should get a sqlite fulltext handler")

    def test_sqlite_save(self):
        """Verify that if we store a bookmark we get the fulltext storage"""
        # first let's add a bookmark we can search on
        self._get_good_request()

        search_res = self.testapp.get('/search?search=bmark&content=1')

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('python' in search_res.body,
                "We should find the python tag in the results: " + search_res.body)
