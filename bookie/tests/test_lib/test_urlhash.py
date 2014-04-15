"""Test the function of the url hash helpers."""
from unittest import TestCase

from bookie.lib.urlhash import generate_hash


class TestUrlHashing(TestCase):
    """Verify UrlHashing works properly"""

    def test_hash_url(self):
        """Hashes base url correctly"""
        url = u'http://google.com'
        hashed = generate_hash(url)
        self.assertEqual('aa2239c17609b2', hashed)

    def test_unicode_url(self):
        """Hashes with unicode correctly"""
        url = u'http://www.bizrevolution.com.br/bizrevolution/2011/02/somos-t\xe3o-jovens-no-campus-party-.html'  # noqa
        hashed = generate_hash(url)
        self.assertEqual('bd846e7222adf2', hashed)
