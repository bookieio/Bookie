from bookie_app.tests import *
from bookie_app.model import meta
from bookie_app.tests import fixtures

from urllib import urlencode

class TestD1Controller(TestController):

    def setUp(self):
        """This is run before every test to provide basic sql data 
        
        All tests have this data available

        """
        fixtures.create_bookmarks()
        fixtures.create_tags()
        fixtures.create_bookmarks_tags()

    def tearDown(self):
        """This is run after every test to clear out any generated data"""
        fixtures.clear_bookmarks()
        fixtures.clear_tags()
        fixtures.clear_bookmarks_tags()

    def test_postadd(self):

        url_data = { 'url': 'http://www.mitechie.com',
            'description': 'My google bookmark',
            'extended': 'Love google',
            'tags': 'search android',
        }

        response = self.app.get(
            url='/d1/posts/add/?%s' % urlencode(url_data),
            params={},
            status=200
        )

        assert 'code="done"' in response, 'Code was not -done-'

        res = meta.Session.execute("SELECT * FROM bookmarks;").fetchall()

        found = False

        for bmark in res:
            if bmark[2] == 'http://www.mitechie.com':
                found = True

        self.assertEquals(found, True)

    def test_postsget_tag(self):
        url_data = { 
            'tag': 'php',
        }

        response = self.app.get(
            url='/d1/posts/get/?%s' % urlencode(url_data),
            params={},
            status=200
        )

        assert 'code="done"' in response, 'Code was not -done-'



