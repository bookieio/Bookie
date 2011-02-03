from bookie_app.model import meta
from bookie_app.model import tags

from bookie_app.model.tags import TagManager, Tag
from bookie_app.model.bookmarks import Bookmark
from bookie_app import model
from bookie_app.tests import fixtures

from unittest import TestCase, main
import logging
log = logging.getLogger('bookie_app')

class TestBookmark(TestCase):

    def setUp(self):
        """This is run before every test to provide basic sql data 
        
        All tests have this data available

        """
        fixtures.create_tags()
        fixtures.create_bookmarks()
        fixtures.create_bookmarks_tags()

    def tearDown(self):
        """This is run after every test to clear out any generated data"""
        fixtures.clear_tags()
        fixtures.clear_bookmarks()
        fixtures.clear_bookmarks_tags()

    def test_getlist(self):
        """The getlist should return a list of tags 
        
        and abide by the limit option
        
        """

        log.debug(meta.metadata.tables)
        taglist = TagManager.get_list()

        self.assertEquals(len(taglist), 3)

        taglist2 = TagManager.get_list(limit=2)
        self.assertEquals(len(taglist2), 2)

    def test_getlist_sorting(self):
        """getlist should also accept sorting parameters


        """
        taglist = TagManager.get_list(order_by=Tag.name, order=model.ORDER_DESC)
        self.assertEquals(taglist[0].name, 'python')

        taglist = TagManager.get_list(order_by=Tag.name)
        self.assertEquals(taglist[0].name, 'php')

        taglist = TagManager.get_list(order_by=Tag.id)
        self.assertEquals(taglist[0].id, 1)

    def test_getlist_byname(self):
        """Test that given a list of names we can get a list of objects back"""
        taglist = TagManager.get_list(tag_names=['pylons', 'php'])
        self.assertEquals(len(taglist), 2)

        for t in taglist:
            self.assertTrue(t.name in ['pylons', 'php'])

    def test_tied_bookmarks(self):
        """Test that we can get the list of bookmarks for a single bookmark"""

        # the bookmark for php should be tied to all three bookmarks
        php = Tag.query.get(3)

        self.assertEquals(php.name, 'php')
        self.assertEquals(len(php.bookmarks), 3)

        bookmarks = [php.bookmarks[0].url, 
                php.bookmarks[1].url,
                php.bookmarks[2].url]
        self.assertTrue('http://google.com' in bookmarks)
        self.assertTrue('http://yahoo.com' in bookmarks)
        self.assertTrue('http://cnn.com' in bookmarks)

    def test_add_tag(self):
        """Given a bookmark adding a tag, make sure the count on the tag is updated"""
        # get the yahoo bookmark
        yahoo = Bookmark.query.get(2)

        # now add the python tag
        py_tag = Tag.query.get(2)
        yahoo.tags.append(py_tag)

        meta.Session.commit()

        # now check that we've got an updated count on tag
        self.assertEquals(py_tag.count, 2)

    def test_remove_tag(self):
        """Given a bookmark removing a tag, make sure the tag count is updated"""
        # get the google bookmark
        google = Bookmark.query.get(1)

        # get the tag for python
        py_tag = Tag.query.get(2)

        # verify that we've got a count of 1 for python since it's only on the
        # google bookmark
        self.assertEquals(py_tag.count, 1)

        # now remove the first tag from it
        del(google.tags[0])

        # commit this change
        meta.Session.commit()

        # now check that we've got an updated count on tag
        self.assertEquals(py_tag.count, 0)

    def test_new_tag_saved(self):
        """Verify that if we parse tags with a tag not in the system it's stored

        """
        tag_string = "python bookie soccer"

        tag_list = TagManager.parse(tag_string)
        meta.Session.commit()

        for tag in tag_list:
            self.assertTrue(isinstance(tag, Tag))

        # and we should now have the base three tags in the system + the two new
        # ones
        count = meta.Session.execute("SELECT COUNT(id) as ct FROM TAGS").fetchall()
        print count
        self.assertEqual(5, count[0][0])

