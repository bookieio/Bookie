"""Test that we're meeting delicious API specifications"""
import logging
import os
import StringIO
import transaction
import unittest

from datetime import datetime

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models.queue import ImportQueue
from bookie.models.queue import ImportQueueMgr
from bookie.lib.urlhash import generate_hash

from bookie.lib.importer import Importer
from bookie.lib.importer import DelImporter
from bookie.lib.importer import DelXMLImporter
from bookie.lib.importer import GBookmarkImporter
from bookie.lib.importer import FBookmarkImporter

from bookie.tests import TestViewBase
from bookie.tests import empty_db


LOG = logging.getLogger(__name__)

API_KEY = None


class TestImports(unittest.TestCase):

    def _delicious_data_test(self):
        """Test that we find the correct set of declicious data after import"""
        # Blatant copy/paste, but I'm on a plane right now so oh well.
        # Now let's do some db sanity checks.
        res = Bmark.query.all()
        self.assertEqual(
            len(res),
            19,
            "We should have 19 results, we got: " + str(len(res)))

        # verify we can find a bookmark by url and check tags, etc
        check_url = u'http://www.ndftz.com/nickelanddime.png'
        check_url_hashed = generate_hash(check_url)
        found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

        self.assertTrue(
            found.hashed.url == check_url, "The url should match our search")
        self.assertEqual(
            len(found.tags),
            7,
            "We should have gotten 7 tags, got: " + str(len(found.tags)))
        self.assertEqual(
            'importer',
            found.inserted_by,
            "The bookmark should have imported: " + found.inserted_by)

        # and check we have a right tag or two
        self.assertTrue(
            'canonical' in found.tag_string(),
            'Canonical should be a valid tag in the bookmark')

        # and check the long description field
        self.assertTrue(
            "description" in found.extended,
            "The extended attrib should have a nice long string in it")

    def _delicious_xml_data_test(self):
        """Test that we find the correct google bmark data after import"""
        res = Bmark.query.all()
        self.assertEqual(
            len(res),
            25,
            "We should have 25 results, we got: " + str(len(res)))

        # verify we can find a bookmark by url and check tags, etc
        check_url = 'http://jekyllrb.com/'
        check_url_hashed = generate_hash(check_url)
        found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

        self.assertTrue(
            found.hashed.url == check_url, "The url should match our search")
        self.assertEqual(
            len(found.tags), 6,
            "We should have gotten 6 tags, got: " + str(len(found.tags)))

        # and check we have a right tag or two
        self.assertTrue(
            'ruby' in found.tag_string(),
            'ruby should be a valid tag in the bookmark')

        # and check the long description field
        self.assertTrue(
            'added for test' in found.extended,
            "'added for test' should be in the extended description")

    def _google_data_test(self):
        """Test that we find the correct google bmark data after import"""
        res = Bmark.query.all()
        self.assertEqual(
            len(res),
            9,
            "We should have 9 results, we got: " + str(len(res)))

        # verify we can find a bookmark by url and check tags, etc
        check_url = 'http://www.alistapart.com/'
        check_url_hashed = generate_hash(check_url)
        found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

        self.assertTrue(
            found.hashed.url == check_url, "The url should match our search")
        self.assertEqual(
            len(found.tags),
            4,
            "We should have gotten 4 tags, got: " + str(len(found.tags)))

        # and check we have a right tag or two
        self.assertTrue(
            'html' in found.tag_string(),
            'html should be a valid tag in the bookmark')

        # and check the long description field
        self.assertTrue(
            "make websites" in found.extended,
            "'make websites' should be in the extended description")

    def _chrome_data_test(self):
        """Test that we find the correct Chrome bmark data after import"""
        res = Bmark.query.all()
        self.assertEqual(
            len(res),
            4,
            "We should have 4 results, we got: " + str(len(res)))

        # Verify we can find a bookmark by url and check tags, etc
        check_url = 'https://addons.mozilla.org/en-US/firefox/bookmarks/'
        check_url_hashed = generate_hash(check_url)
        found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

        self.assertTrue(
            found.hashed.url == check_url, "The url should match our search")
        self.assertEqual(
            len(found.tags),
            2,
            "We should have gotten 2 tags, got: " + str(len(found.tags)))

        # and check we have a right tag or two
        self.assertTrue(
            'imported-from-firefox' in found.tag_string(),
            'imported-from-firefox should be a valid tag in the bookmark')

        # and check the timestamp is correct
        # relative to user's timezone
        date_should_be = datetime.fromtimestamp(1350353334)
        self.assertEqual(date_should_be, found.stored)

    def _firefox_data_test(self):
        """Verify we find the correct firefox backup bmark data after import"""
        res = Bmark.query.all()
        self.assertEqual(
            len(res),
            13,
            "We should have 13 results, we got: " + str(len(res)))

        # Verify we can find a bookmark by url and check tags, etc
        check_url = 'https://github.com/bookieio/Bookie'
        check_url_hashed = generate_hash(check_url)
        found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

        self.assertTrue(
            found.hashed.url == check_url, "The url should match our search")
        self.assertEqual(
            len(found.tags),
            2,
            "We should have gotten 2 tags, got: " + str(len(found.tags)))

        # and check we have a right tag or two
        self.assertTrue(
            'myfav' in found.tag_string(),
            'myfav should be a valid tag in the bookmark')

        # and check the timestamp is correct
        # relative to user's timezone
        date_should_be = datetime.fromtimestamp(1394649032847102/1e6)
        self.assertEqual(date_should_be, found.stored)


class ImporterBaseTest(TestImports):
    """Verify the base import class is working"""

    def test_doesnt_implement_can_handle(self):
        """Verify we get the exception expected when running can_handle"""
        self.assertRaises(NotImplementedError, Importer.can_handle, "")

    def test_doesnt_implement_process(self):
        """Verify we get the exception expected when running process"""
        some_io = StringIO.StringIO()
        imp = Importer(some_io)
        self.assertRaises(NotImplementedError, imp.process)

    def test_factory_gives_delicious(self):
        """"Verify that the base importer will give DelImporter"""
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'delicious.html')

        with open(del_file) as del_io:
            imp = Importer(del_io, username=u"admin")

            self.assertTrue(
                isinstance(imp, DelImporter),
                "Instance should be a delimporter instance")

    def test_factory_gives_google(self):
        """"Verify that the base importer will give GBookmarkImporter"""
        loc = os.path.dirname(__file__)
        google_file = os.path.join(loc, 'googlebookmarks.html')

        with open(google_file) as google_io:
            imp = Importer(google_io, username=u"admin")

            self.assertTrue(
                isinstance(imp, GBookmarkImporter),
                "Instance should be a GBookmarkImporter instance")


class ImportDeliciousTest(TestImports):
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
        empty_db()

    def test_is_delicious_file(self):
        """Verify that this is a delicious file"""
        good_file = self._get_del_file()

        self.assertTrue(
            DelImporter.can_handle(good_file),
            "DelImporter should handle this file")

        good_file.close()

    def test_is_not_delicious_file(self):
        """And that it returns false when it should"""
        bad_file = StringIO.StringIO()
        bad_file.write('failing tests please')
        bad_file.seek(0)

        self.assertTrue(
            not DelImporter.can_handle(bad_file),
            "DelImporter cannot handle this file")

        bad_file.close()

    def test_import_process(self):
        """Verify importer inserts the correct records"""
        good_file = self._get_del_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        # now let's do some db sanity checks
        self._delicious_data_test()

    def test_dupe_imports(self):
        """If we import twice, we shouldn't end up with duplicate bmarks"""
        good_file = self._get_del_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        good_file = self._get_del_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        # now let's do some db sanity checks
        self._delicious_data_test()


class ImportDeliciousXMLTest(TestImports):
    """Test the Bookie XML version importer for delicious"""

    def _get_del_file(self):
        """We need to get the locally found delicious.html file for tests"""
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'newdelicious.xml')
        return open(del_file)

    def tearDown(self):
        """Regular tear down method"""
        empty_db()

    def test_is_delicious_file(self):
        """Verify that this is a delicious file"""
        good_file = self._get_del_file()
        self.assertTrue(
            DelXMLImporter.can_handle(good_file),
            "DelXMLImporter should handle this file")
        good_file.close()

    def test_is_not_delicious_file(self):
        """And that it returns false when it should"""
        bad_file = StringIO.StringIO()
        bad_file.write('failing tests please')
        bad_file.seek(0)

        self.assertTrue(
            not DelXMLImporter.can_handle(bad_file),
            "DelXMLImporter cannot handle this file")

        bad_file.close()

    def test_import_process(self):
        """Verify importer inserts the correct records"""
        good_file = self._get_del_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        # now let's do some db sanity checks
        self._delicious_xml_data_test()

    def test_dupe_imports(self):
        """If we import twice, we shouldn't end up with duplicate bmarks"""
        good_file = self._get_del_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        good_file = self._get_del_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        # Now let's do some db sanity checks.
        self._delicious_xml_data_test()


class ImportGoogleTest(TestImports):
    """Test the Bookie importer for google bookmarks"""

    def _get_google_file(self):
        """We need to get the locally found delicious.html file for tests"""
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'googlebookmarks.html')

        return open(del_file)

    def tearDown(self):
        """Regular tear down method"""
        empty_db()

    def test_is_google_file(self):
        """Verify that this is a delicious file"""
        good_file = self._get_google_file()

        self.assertTrue(
            GBookmarkImporter.can_handle(good_file),
            "GBookmarkImporter should handle this file")

        good_file.close()

    def test_is_not_google_file(self):
        """And that it returns false when it should"""
        bad_file = StringIO.StringIO()
        bad_file.write('failing tests please')

    def test_import_process(self):
        """Verify importer inserts the correct google bookmarks"""
        good_file = self._get_google_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        # now let's do some db sanity checks
        self._google_data_test()

    def test_bookmarklet_file(self):
        """Verify we can import a file with a bookmarklet in it."""
        loc = os.path.dirname(__file__)
        bmarklet_file = os.path.join(loc, 'bookmarklet_error.htm')
        fh = open(bmarklet_file)

        imp = Importer(fh, username=u"admin")
        imp.process()

        res = Bmark.query.all()
        self.assertEqual(len(res), 3)


class ImportChromeTest(TestImports):
    """Test the Bookie importer for Chrome export"""

    def _get_file(self):
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'chrome.html')

        return open(del_file)

    def tearDown(self):
        """Regular tear down method"""
        empty_db()

    def test_is_google_file(self):
        """Verify that this is a delicious file"""
        good_file = self._get_file()

        self.assertTrue(
            GBookmarkImporter.can_handle(good_file),
            "GBookmarkImporter should handle this file")

        good_file.close()

    def test_is_not_google_file(self):
        """And that it returns false when it should"""
        bad_file = StringIO.StringIO()
        bad_file.write('failing tests please')
        bad_file.seek(0)

        self.assertTrue(
            not GBookmarkImporter.can_handle(bad_file),
            "GBookmarkImporter cannot handle this file")

        bad_file.close()

    def test_import_process(self):
        """Verify importer inserts the correct google bookmarks"""
        good_file = self._get_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        # now let's do some db sanity checks
        self._chrome_data_test()


class ImportFirefoxTest(TestImports):
    """Test the Bookie importer for Firefox backup export"""

    def _get_file(self):
        loc = os.path.dirname(__file__)
        del_file = os.path.join(loc, 'firefox_backup.json')

        return open(del_file)

    def tearDown(self):
        """Regular tear down method"""
        empty_db()

    def test_is_firefox_file(self):
        """Verify that this is a firefox json file"""
        good_file = self._get_file()

        self.assertTrue(
            FBookmarkImporter.can_handle(good_file),
            "FBookmarkImporter should handle this file")

        good_file.close()

    def test_is_not_firefox_file(self):
        """And that it returns false when it should"""
        bad_file = StringIO.StringIO()
        bad_file.write('failing tests please')
        bad_file.seek(0)

        self.assertTrue(
            not FBookmarkImporter.can_handle(bad_file),
            "FBookmarkImporter cannot handle this file")

        bad_file.close()

    def test_import_process(self):
        """Verify importer inserts the correct firefox bookmarks"""
        good_file = self._get_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        # now let's do some db sanity checks
        self._firefox_data_test()

    def test_nested_folder(self):
        """Verify if bookmarks in nested folders are imported"""
        good_file = self._get_file()
        imp = Importer(good_file, username=u"admin")
        imp.process()

        check_url = 'https://github.com/bookieio/Bookie/issues/71'
        check_url_hashed = generate_hash(check_url)
        found = Bmark.query.filter(Bmark.hash_id == check_url_hashed).one()

        self.assertTrue(
            found.hashed.url == check_url, "The url should match our search")


class ImportViews(TestViewBase):
    """Test the web import"""

    def _upload(self):
        """Make an upload to the importer"""
        loc = os.path.dirname(__file__)
        del_file = open(os.path.join(loc, 'delicious.html'))
        res = self.app.post(
            '/admin/import',
            params={'api_key': self.api_key},
            upload_files=[('import_file',
                           'delicious.html',
                           del_file.read())],
        )
        return res

    def test_import_upload(self):
        """After we upload a file, we should have an importer queue."""
        self._login_admin()

        # verify we get the form
        res = self.app.get('/admin/import')
        self.assertTrue(
            '<form' in res.body,
            'Should have a form in the body for submitting the upload')

        res = self._upload()

        self.assertEqual(
            res.status,
            "302 Found",
            msg='Import status is 302 redirect by home, ' + res.status)

        # now verify that we've got our record
        imp = ImportQueueMgr.get_ready()
        imp = imp[0]
        self.assertTrue(imp, 'We should have a record')
        self.assertTrue(imp.file_path.endswith('admin.delicious.html'))
        self.assertEqual(imp.status, 0, 'start out as default status of 0')

    def test_skip_running(self):
        """Verify that if running, it won't get returned again"""
        self._login_admin()
        res = self._upload()

        self.assertEqual(
            res.status,
            "302 Found",
            msg='Import status is 302 redirect by home, ' + res.status)

        # now verify that we've got our record
        imp = ImportQueueMgr.get_ready()
        imp = imp[0]
        imp.status = 2
        DBSession.flush()

        imp = ImportQueueMgr.get_ready()
        self.assertTrue(not imp, 'We should get no results back')

    def test_one_import(self):
        """You should be able to only get one import running at a time"""
        self._login_admin()

        # Prep the db with 2 other imports ahead of this user's.
        # We have to commit these since the request takes place in a new
        # session/transaction.
        DBSession.add(ImportQueue(username=u'testing',
                                  file_path=u'testing.txt'))
        DBSession.add(ImportQueue(username=u'testing2',
                                  file_path=u'testing2.txt'))
        DBSession.flush()
        transaction.commit()

        res = self._upload()
        res.follow()

        # now let's hit the import page, we shouldn't get a form, but instead a
        # message about our import
        res = self.app.get('/admin/import')

        self.assertTrue('<form' not in res.body, "We shouldn't have a form")
        self.assertTrue(
            'waiting in the queue' in res.body,
            "We want to display a waiting message.")
        self.assertTrue(
            '2 other imports' in res.body,
            "We want to display a count message." + res.body)

    def test_completed_dont_count(self):
        """Once completed, we should get the form again"""
        self._login_admin()

        # add out completed one
        q = ImportQueue(
            username=u'admin',
            file_path=u'testing.txt'
        )
        q.completed = datetime.now()
        q.status = 2
        DBSession.add(q)
        transaction.commit()

        # now let's hit the import page, we shouldn't get a form, but instead a
        # message about our import
        res = self.app.get('/admin/import')

        self.assertTrue('<form' in res.body, "We should have a form")

    def test_empty_upload(self):
        """Verify if error message is shown if no file is tried to upload"""
        self._login_admin()

        res = self.app.post(
            '/admin/import',
            params={'api_key': self.api_key},
            upload_files=[],
        )
        self.assertTrue(
            'Please provide a file to import' in res.body,
            "Error message should be present")
