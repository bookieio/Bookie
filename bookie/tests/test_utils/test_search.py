"""Test if correct arguments are passed to Whoosh to search
indexed content

"""
from mock import patch
from pyramid import testing
from unittest import TestCase


class TestSearchAttr(TestCase):

    attr = []

    def _return_attr(self, *args, **kwargs):
        """Saves arguments passed to WhooshFulltext
        search function to attr

        """
        self.attr = [args, kwargs]
        return []

    def setUp(self):
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @patch('bookie.models.fulltext.WhooshFulltext')
    def test_search_content(self, mock_search):
        """Test if correct arguments are passed to WhooshFulltext if
        searched through webui"""
        mock_search().search.side_effect = self._return_attr
        self.testapp.get('/results/bookie')

        self.assertTrue(mock_search.called)
        self.assertEqual(self.attr[0][0],
                         'bookie',
                         'search term should be bookie')
        self.assertTrue(self.attr[1]['content'])

    @patch('bookie.models.fulltext.WhooshFulltext')
    def test_search_content_ajax(self, mock_search):
        """Test if correct arguments are passed to WhooshFulltext
        with ajax request"""
        mock_search().search.side_effect = self._return_attr
        self.testapp.get(url='/results/ajax', xhr=True)

        self.assertTrue(mock_search.called)
        self.assertEqual(self.attr[0][0],
                         'ajax',
                         'search term should be ajax')
        self.assertTrue(self.attr[1]['content'])
