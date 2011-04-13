"""Test the fulltext implementation"""
import logging
import os

from nose.tools import ok_
from unittest import TestCase

from bookie.lib.readable import ReadContent
from bookie.lib.readable import ReadUrl

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

