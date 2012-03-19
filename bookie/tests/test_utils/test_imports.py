"""Test that we're meeting delicious API specifications"""
import logging
import os
import StringIO
import transaction
import unittest

from datetime import datetime
from nose.tools import ok_
from nose.tools import eq_
from nose.tools import raises

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Tag, bmarks_tags
from bookie.models.queue import ImportQueue
from bookie.models.queue import ImportQueueMgr
from bookie.lib.urlhash import generate_hash

from bookie.lib.importer import Importer
from bookie.lib.importer import DelImporter
from bookie.lib.importer import GBookmarkImporter

from bookie.tests import TestViewBase


LOG = logging.getLogger(__name__)

API_KEY = None


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
    eq_('importer', found.inserted_by,
        "The bookmark should have come from importing: " + found.inserted_by)

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
            imp = Importer(del_io, username="admin")

            ok_(isinstance(imp, DelImporter),
                    "Instance should be a delimporter instance")

    def test_factory_gives_google(self):
        """"Verify that the base importer will give GBookmarkImporter"""
        loc = os.path.dirname(__file__)
        google_file = os.path.join(loc, 'googlebookmarks.html')

        with open(google_file) as google_io:
            imp = Importer(google_io, username="admin")

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
        imp = Importer(good_file, username="admin")
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
        imp = Importer(good_file, username="admin")
        imp.process()

        # now let's do some db sanity checks
        _google_data_test()


class ImportViews(TestViewBase):
    """Test the web import"""

    def _login(self):
        """Make the login call to the app"""
        self.app.post('/login',
                            params={
                                "login": "admin",
                                "password": "admin",
                                "form.submitted": "Log In",
                            },
                            status=302)

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
        self._login()

        # verify we get the form
        res = self.app.get('/admin/import')
        ok_('<form' in res.body,
            'Should have a form in the body for submitting the upload')

        res = self._upload()

        eq_(res.status, "302 Found",
            msg='Import status is 302 redirect by home, ' + res.status)

        # now verify that we've got our record
        imp = ImportQueueMgr.get_ready()
        imp = imp[0]
        ok_(imp, 'We should have a record')
        eq_(imp.file_path, 'delicious.html')
        eq_(imp.status, 0, 'start out as default status of 0')

    def test_skip_running(self):
        """Verify that if running, it won't get returned again"""
        self._login()
        res = self._upload()

        eq_(res.status, "302 Found",
            msg='Import status is 302 redirect by home, ' + res.status)

        # now verify that we've got our record
        imp = ImportQueueMgr.get_ready()
        imp = imp[0]
        imp.status=2
        DBSession.flush()

        imp = ImportQueueMgr.get_ready()
        ok_(not imp, 'We should get no results back')

    def test_one_import(self):
        """You should be able to only get one import running at a time"""
        self._login()

        # Prep the db with 2 other imports ahead of this user's.
        # We have to commit these since the request takes place in a new
        # session/transaction.
        DBSession.add(ImportQueue(username='testing', file_path='testing.txt'))
        DBSession.add(ImportQueue(username='testing2', file_path='testing2.txt'))
        DBSession.flush()
        transaction.commit()

        res = self._upload()
        res.follow()

        # now let's hit the import page, we shouldn't get a form, but instead a
        # message about our import
        res = self.app.get('/admin/import')

        ok_('<form' not in res.body, "We shouldn't have a form")
        ok_('waiting in the queue' in res.body, "We want to display a waiting message.")
        ok_('2 other imports' in res.body, "We want to display a count message." + res.body)

    def test_completed_dont_count(self):
        """Once completed, we should get the form again"""
        self._login()

        # add out completed one
        q = ImportQueue(
            username='admin',
            file_path='testing.txt'
        )
        q.completed = datetime.now()
        q.status = 2
        DBSession.add(q)
        transaction.commit()

        # now let's hit the import page, we shouldn't get a form, but instead a
        # message about our import
        res = self.app.get('/admin/import')

        ok_('<form' in res.body, "We should have a form")

