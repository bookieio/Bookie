"""Test the fulltext implementation"""
from nose.tools import ok_
from unittest import TestCase

from bookie.lib.readable import Readable
from bookie.lib.readable import ReadContent
from bookie.lib.readable import ReadUrl


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

