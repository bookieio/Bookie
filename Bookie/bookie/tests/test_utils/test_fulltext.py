"""Test the fulltext implementation"""
from nose.tools import ok_
from unittest import TestCase

from bookie.models.fulltext import get_fulltext_handler
from bookie.models.fulltext import SqliteFulltext

class TestFulltext(TestCase):
    """Test that our fulltext classes function"""

    def setUp(self):
        """Setup Tests"""
        pass

    def tearDown(self):
        """Tear down each test"""
        pass


    def test_get_handler(self):
        """Verify we get the right type of full text store object"""
        sqlite_str = "sqlite:///somedb.db"

        handler = get_fulltext_handler(sqlite_str)

        ok_(isinstance(handler, SqliteFulltext),
                "Should get a sqlite fulltext handler")
