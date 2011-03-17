"""Test that we're meeting delicious API specifications"""
import os
import StringIO
import transaction
import unittest
from nose.tools import ok_, raises

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Tag, bmarks_tags

from bookie.lib.importer import Importer
from bookie.lib.importer import DelImporter
from bookie.lib.importer import GBookmarkImporter


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
        bad_file.seek(0)

        ok_(not GBookmarkImporter.can_handle(bad_file),
            "GBookmarkImporter cannot handle this file")

        bad_file.close()
