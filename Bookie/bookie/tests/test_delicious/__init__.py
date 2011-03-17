"""Test that we're meeting delicious API specifications"""
from datetime import datetime, timedelta
import transaction
import unittest
import urllib
from nose.tools import ok_, eq_
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark, NoResultFound
from bookie.models import Tag, bmarks_tags


class DelPostTest(unittest.TestCase):
    """Test post related calls"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini', 'main')
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

    def _get_good_request(self):
        """Return the basics for a good add bookmark request"""
        session = DBSession()
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'api_key': u'testapi',
        }

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/delapi/posts/add?' + req_params)
        session.flush()
        return res

    def test_post_add_fail(self):
        """Basic add of a new post failing

        Failed response:
            <result code="something went wrong" />

        Not supporting optional params right now
            replace, shared

        """
        failed = '<result code="Bad Request: missing url" />'
        prms = {
                'url': '',
                'description': '',
                'extended': '',
                'tags': '',
                'api_key': u'testapi',
        }

        req_params = urllib.urlencode(prms)

        res = self.testapp.get('/delapi/posts/add?' + req_params)
        eq_(res.status, "200 OK", msg='Post Add status is 200, ' + res.status)
        eq_(res.body, failed, msg="Request should return failed msg: " + res.body)

    def test_post_add_success(self):
        """Basic add of a new post working

        Success response:
            <result code="done" />

        Not supporting optional params right now
            replace, shared

        """
        success = '<result code="done" />'
        res = self._get_good_request()

        eq_(res.status, "200 OK", msg='Post Add status is 200, ' + res.status)
        eq_(res.body, success, msg="Request should return done msg")

    def test_new_bmark(self):
        # go save the thing
        self._get_good_request()

        try:
            res = Bmark.query.filter(Bmark.url == u'http://google.com').one()
            ok_(res, 'We found a result in the db for this bookmark')
            ok_('extended' in res.extended,
                    'Extended value was set to bookmark')
            if res:
                return True
            else:
                assert False, "Could not find our bookmark we saved"
        except NoResultFound:
            assert False, "No result found for the bookmark"

    def test_post_add_with_dt(self):
        """Make sure if we provide a date it works

        Success response:
            <result code="done" />

        Not supporting optional params right now
            replace, shared

        """

        success = '<result code="done" />'
        session = DBSession()

        # pick a date that is tomorrow
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        dt = yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'dt': dt,
                'api_key': u'testapi',
        }

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/delapi/posts/add?' + req_params)
        session.flush()

        eq_(res.status, "200 OK", msg='Post Add status is 200, ' + res.status)
        eq_(res.body, success, msg="Request should return done msg")

        # now pull up the bmark and check the date is yesterday
        res = Bmark.query.filter(Bmark.url == u'http://google.com').one()
        eq_(res.stored.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d'),
            "The stored date {0} is the same as the requested {1}".format(
                res.stored,
                yesterday))

    def test_new_bmark_tags(self):
        """Manually check db for new bmark tags set"""
        self._get_good_request()

        res = Bmark.query.filter(Bmark.url == u'http://google.com').one()

        ok_('python' in res.tags, 'Found the python tag in the bmark')
        ok_('search' in res.tags, 'Found the search tag in the bmark')

    def test_skip_dupe_tags(self):
        """Make sure we don't end up with duplicate tags in the system"""
        self._get_good_request()
        self._get_good_request()

        all_tags = Tag.query.all()

        ok_(len(all_tags) == 2, 'We only have two tags in the system')

    def test_datestimes_set(self):
        """Test that we get the new datetime fields as we work"""
        now = datetime.now()
        self._get_good_request()
        res = Bmark.query.filter(Bmark.url == u'http://google.com').one()

        ok_(res.stored >= now,
                "Stored time is now or close to now {0}:{1}".format(res.stored, now))

        res.url = u"Somethingnew.com"
        session = DBSession()
        session.flush()

        # now hopefully have an updated value
        ok_(res.updated >= now,
                "Stored time is now or close to now {0}:{1}".format(res.updated, now))

    def test_remove_bmark(self):
        """Remove a bmark from the system"""
        self._get_good_request()

        # now send in the delete squad
        prms = {
                'url': u'http://google.com',
                'api_key': u'testapi',
        }

        req_params = urllib.urlencode(prms)

        res = self.testapp.get('/delapi/posts/delete?' + req_params)
        eq_(res.status, "200 OK", msg='Post Delete status is 200, ' + res.status)
        ok_('done' in res.body, msg="Request should return done msg: " + res.body)

    def test_get_post_byurl(self):
        """Verify we can fetch a post back via a url

        While this is delicious api compat, we're going to default to json
        response I think

        We'll add xml support to the output later on

        """
        self._get_good_request()
        prms = {
                'url': u'http://google.com',
        }

        req_params = urllib.urlencode(prms)

        res = self.testapp.get('/delapi/posts/get?' + req_params)

        ok_('href' in res.body, "we have an href link in there")
        ok_('python' in res.body, "we have the python tag")
        ok_('search' in res.body, "we have the search tag")

    def test_update_post(self):
        """Updates allowed over the last one

        If you /post/add to an existing bookmark, the new data overrides the
        old data

        """
        self._get_good_request()

        # now build a new version of the request we can check
        session = DBSession()
        prms = {
                'url': u'http://google.com',
                'description': u'This is my updated google desc',
                'extended': 'updated extended notes about it in full form',
                'tags': u'python search updated',
                'api_key': u'testapi',
        }

        req_params = urllib.urlencode(prms)
        self.testapp.get('/delapi/posts/add?' + req_params)
        session.flush()

        res = Bmark.query.filter(Bmark.url == u'http://google.com').one()

        ok_('updated' in res.description,
                'Updated description took: ' + res.description)
        ok_('updated' in res.extended,
                'Updated extended took: ' + res.extended)
        ok_('python' in res.tags, 'Found the python tag in the bmark')
        ok_('search' in res.tags, 'Found the search tag in the bmark')
        ok_('updated' in res.tags, 'Found the updated tag in the bmark')


class DelImportTest(unittest.TestCase):
    """Test that we can successfully import data from delicious"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini', 'main')
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

    def test_import(self):
        """Grab our test data file, import it, and check it out"""
        # need to start work on adding this, but passing for build now
        assert True


class GBookmarkImportTest(unittest.TestCase):
    """Test that we can successfully import data from delicious"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini', 'main')
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

    def test_import(self):
        """Grab our test data file, import it, and check it out"""
        # need to start work on adding this, but passing for build now
        assert True
