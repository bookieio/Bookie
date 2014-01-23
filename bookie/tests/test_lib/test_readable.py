"""Test the function of the readable library."""
from unittest import TestCase

from bookie.lib import readable


class TestReadUrl(TestCase):
    """Verify ReadUrl functions"""

    def setUp(self):
        """Setup Tests"""
        pass

    def tearDown(self):
        """Tear down each test"""
        pass

    def test_parse_malformed_url(self):
        """Properly error on an unparseable url."""
        url = u'http://whttp://lucumr.pocoo.org/2012/8/5/stateless-and-proud/'
        read = readable.ReadUrl.parse(url)
        self.assertEqual(read.status, 901)

    def test_unfetchable_url(self):
        """Cannot fetch content for unreadable urls.

        Urls that are with:

            chrome://
            file://

        etc, cannot have their content fetched so don't bother.

        """
        url = u'file://test.html'
        read = readable.ReadUrl.parse(url)
        self.assertEqual(read.status, 901)
