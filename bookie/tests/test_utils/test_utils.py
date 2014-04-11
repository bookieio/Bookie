from unittest import TestCase

from bookie.lib.utils import suggest_tags


class TestSuggestTags(TestCase):
    """Verify we can suggest tags for content."""

    def test_avoids_bombing_on_none(self):
        """It should not bomb when passed None"""
        test_value = None
        self.assertEqual(set(), suggest_tags(test_value))

    def test_returns_nouns_for_string(self):
        """It returns only nouns from the strings."""
        test_value = 'google drives autonomous cars'
        self.assertEqual(
            set([u'cars', u'autonomous']),
            suggest_tags(test_value))

    def test_splits_urls_for_nouns(self):
        """It pulls nouns from a url string."""
        test_value = "http://google.com/drives/autonomous/cars"
        self.assertEqual(
            set([u'cars', u'autonomous']),
            suggest_tags(test_value))

    def test_splits_url_parts(self):
        """- and _ should be good split points"""
        test_value = "http://google.com/drives-autonomous_cars"
        self.assertEqual(
            set([u'cars', u'autonomous']),
            suggest_tags(test_value))
