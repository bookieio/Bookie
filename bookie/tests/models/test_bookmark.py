from bookie_app.model import meta
from bookie_app.model import bookmarks

from bookie_app.model.bookmarks import BookmarkManager, Bookmark
from bookie_app import model
from bookie_app.tests import fixtures

from unittest import TestCase, main

class TestBookmark(TestCase):

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

    def test_init(self):
        """On init the url should be hashed for using later on"""
        bmark = bookmarks.Bookmark('http://google.com')

        self.assertEquals(bmark.hash,
                '234988566c9a0a9cf952cec82b143bf9c207ac16')

    def test_getlist(self):
        """The getlist should return a list of bookmarks 
        
        and abide by the limit option
        
        """
        blist = BookmarkManager.get_list()

        self.assertEquals(len(blist), 3)

        blist2 = BookmarkManager.get_list(limit=2)
        self.assertEquals(len(blist2), 2)

    def test_getlist_sorting(self):
        """getlist should also accept sorting parameters


        """
        blist = BookmarkManager.get_list(order_by=Bookmark.url, order=model.ORDER_DESC)
        self.assertEquals(blist[0].url, 'http://yahoo.com')

        blist = BookmarkManager.get_list(order_by=Bookmark.url)
        self.assertEquals(blist[0].url, 'http://cnn.com')

        blist = BookmarkManager.get_list(order_by=Bookmark.added)
        self.assertEquals(blist[0].url, 'http://google.com')

    def test_tied_tags(self):
        """Test that we can get the list of tags for a single bookmark"""

        # the bookmark for yahoo should be tied to the php and pylons tags
        yahoo = Bookmark.query.get(2)

        self.assertEquals(yahoo.url, 'http://yahoo.com')
        self.assertEquals(len(yahoo.tags), 2)

        tags = [yahoo.tags[0].name, yahoo.tags[1].name]
        self.assertTrue('php' in tags)
        self.assertTrue('pylons' in tags)

    def test_tied_list_tags(self):
        """Test that we can get the bookmarks with the tags data"""

        blist = BookmarkManager.get_list(with_tags=True)

        for b in blist:
            self.assertTrue(len(b.tags) > 0)
