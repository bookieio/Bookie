"""Test that we're meeting delicious API specifications"""
import logging
import os
import StringIO
import transaction
import unittest

from nose.tools import ok_
from nose.tools import eq_
from nose.tools import raises
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Tag, bmarks_tags
from bookie.lib.urlhash import generate_hash

from bookie.lib.importer import Importer
from bookie.lib.importer import DelImporter
from bookie.lib.importer import GBookmarkImporter

LOG = logging.getLogger(__name__)


def _delicious_data_test():
    """Test that we find the correct set of declicious data after import"""
    # blatant copy/paste, but I'm ona plane right now so oh well
    # now let's do some db sanity checks
    res = Bmark.query.all()
    eq_(len(res), 19,
        "We should have 19 results, we got: " + str(len(res)))

    # verify we can find a bookmark by url and check tags, etc
    check_url = 'http://www.ndftz.com/nickelanddime.png'
    check_url_hashed = generate_hash(check_url)
    found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

    ok_(found.hashed.url == check_url, "The url should match our search")
    eq_(len(found.tags), 7,
        "We should have gotten 7 tags, got: " + str(len(found.tags)))

    # and check we have a right tag or two
    ok_('canonical' in found.tag_string(),
            'Canonical should be a valid tag in the bookmark')

    # and check the long description field
    ok_("description" in found.extended,
        "The extended attrib should have a nice long string in it")


def _google_data_test():
    """Test that we find the correct google bmark data after import"""
    res = Bmark.query.all()
    eq_(len(res), 10,
        "We should have 10 results, we got: " + str(len(res)))

    # verify we can find a bookmark by url and check tags, etc
    check_url = 'http://www.alistapart.com/'
    check_url_hashed = generate_hash(check_url)
    found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

    ok_(found.hashed.url == check_url, "The url should match our search")
    eq_(len(found.tags), 4,
        "We should have gotten 4 tags, got: " + str(len(found.tags)))

    # and check we have a right tag or two
    ok_('html' in found.tag_string(),
            'html should be a valid tag in the bookmark')

    # and check the long description field
    ok_("make websites" in found.extended,
        "'make websites' should be in the extended description")


class ImporterBaseTest(unittest.TestCase):
    """Verify the base import class is working"""

    @raises(NotImplementedError)
    def test_doesnt_implement_can_handle(self):
        """Verify we get the exception expected when running can_handle"""
        Importer.can_handle("")

    @raises(NotImplementedError)
    def test_doesnt_implement_process(self):
        """Verify we get the exception expected when running process"""
        some_io = StringIO.StringIO()
        imp = Importer(some_io)
        imp.process()

    def test_factory_gives_delicious(self):
        """"Verify that the base importer will give DelImporter"""
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'delicious.html')

        with open(del_file) as del_io:
            imp = Importer(del_io)

            ok_(isinstance(imp, DelImporter),
                    "Instance should be a delimporter instance")

    def test_factory_gives_google(self):
        """"Verify that the base importer will give GBookmarkImporter"""
        loc = os.path.dirname(__file__)
        google_file = os.path.join(loc, 'googlebookmarks.html')

        with open(google_file) as google_io:
            imp = Importer(google_io)

            ok_(isinstance(imp, GBookmarkImporter),
                    "Instance should be a GBookmarkImporter instance")


class ImportDeliciousTest(unittest.TestCase):
    """Test the Bookie importer for delicious"""

    def _get_del_file(self):
        """We need to get the locally found delicious.html file for tests"""
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'delicious.html')

        return open(del_file)

    def setUp(self):
        """Regular setup hooks"""
        pass

    def tearDown(self):
        """Regular tear down method"""
        session = DBSession()
        Bmark.query.delete()
        Tag.query.delete()
        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()

    def test_is_delicious_file(self):
        """Verify that this is a delicious file"""
        good_file = self._get_del_file()

        ok_(DelImporter.can_handle(good_file),
            "DelImporter should handle this file")

        good_file.close()

    def test_is_not_delicious_file(self):
        """And that it returns false when it should"""
        bad_file = StringIO.StringIO()
        bad_file.write('failing tests please')
        bad_file.seek(0)

        ok_(not DelImporter.can_handle(bad_file),
            "DelImporter cannot handle this file")

        bad_file.close()

    def test_import_process(self):
        """Verify importer inserts the correct records"""
        good_file = self._get_del_file()
        imp = Importer(good_file)
        imp.process()

        # now let's do some db sanity checks
        _delicious_data_test()


class ImportGoogleTest(unittest.TestCase):
    """Test the Bookie importer for google bookmarks"""

    def _get_google_file(self):
        """We need to get the locally found delicious.html file for tests"""
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'googlebookmarks.html')

        return open(del_file)

    def tearDown(self):
        """Regular tear down method"""
        session = DBSession()
        Bmark.query.delete()
        Tag.query.delete()
        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()

    def test_is_google_file(self):
        """Verify that this is a delicious file"""
        good_file = self._get_google_file()

        ok_(GBookmarkImporter.can_handle(good_file),
            "GBookmarkImporter should handle this file")

        good_file.close()

    def test_is_not_google_file(self):
        """And that it returns false when it should"""
        bad_file = StringIO.StringIO()
        bad_file.write('failing tests please')

    def test_import_process(self):
        """Verify importer inserts the correct google bookmarks"""
        good_file = self._get_google_file()
        imp = Importer(good_file)
        imp.process()

        # now let's do some db sanity checks
        _google_data_test()


class ImportViews(unittest.TestCase):
    """Test the web import"""

    def setUp(self):
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()
        session = DBSession()
        Bmark.query.delete()
        Tag.query.delete()
        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()

    def test_delicious_import(self):
        """Test that we can upload/import our test file"""
        session = DBSession()
        loc = os.path.dirname(__file__)
        del_file = open(os.path.join(loc, 'delicious.html'))

        post = {
            'api_key': 'testapi',
        }

        res = self.testapp.post('/import',
                                params=post,
                                upload_files=[('import_file',
                                               'delicious.html',
                                               del_file.read())],
        )

        eq_(res.status, "302 Found",
            msg='Import status is 302 redirect by home, ' + res.status)

        session.flush()

        # test all the data we want to test after the import
        _delicious_data_test()

    def test_google_import(self):
        """Test that we can upload our google file"""
        session = DBSession()
        loc = os.path.dirname(__file__)
        del_file = open(os.path.join(loc, 'googlebookmarks.html'))

        post = {
            'api_key': 'testapi',
        }

        res = self.testapp.post('/import',
                                params=post,
                                upload_files=[('import_file',
                                               'googlebookmarks.html',
                                               del_file.read())],
        )

        eq_(res.status, "302 Found",
            msg='Import status is 302 redirect by home, ' + res.status)

        session.flush()

        # test all the data we want to test after the import
        _google_data_test()
