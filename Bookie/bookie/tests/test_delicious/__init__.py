"""Test that we're meeting delicious API specifications"""
from datetime import datetime
import transaction
import unittest
import urllib
from nose.tools import ok_, eq_
from bookie.tests import settings, global_config

from bookie.models import DBSession
from bookie.models import Bmark, NoResultFound
from bookie.models import Tag


class DelPostTest(unittest.TestCase):
    """Test post related calls"""

    def setUp(self):
        from bookie import main
        app = main(global_config, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        transaction.begin()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        session = DBSession()
        session.execute('DELETE FROM bmarks')
        session.execute('DELETE FROM tags')
        session.execute('DELETE FROM bmark_tags')
        transaction.commit()

    def _get_good_request(self):
        """Return the basics for a good add bookmark request"""
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
        }

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/delapi/posts/add?' + req_params)

        return res

    def test_post_add_fail(self):
        """Basic add of a new post failing

        Failed response:
            <result code="something went wrong" />

        Not supporting optional params right now
            dt, replace, shared

        """
        failed = '<result code="Bad Request: missing url" />'
        prms = {
                'url': '',
                'description': '',
                'extended': '',
                'tags': '',
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
            dt, replace, shared

        """
        success = '<result code="done" />'
        res = self._get_good_request()

        eq_(res.status, "200 OK", msg='Post Add status is 200, ' + res.status)
        eq_(res.body, success, msg="Request should return done msg")

    def test_new_bmark(self):
        # go save the thing
        self._get_good_request()

        try:
            res = Bmark.query.filter(Bmark.url == u'google.com').one()
            ok_(res, 'We found a result in the db for this bookmark')
            if res:
                return True
            else:
                assert False, "Could not find our bookmark we saved"
        except NoResultFound:
            assert False, "No result found for the bookmark"

    def test_new_bmark_tags(self):
        """Manually check db for new bmark tags set"""
        self._get_good_request()

        res = Bmark.query.filter(Bmark.url == unicode('google.com')).one()

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
        res = Bmark.query.filter(Bmark.url == unicode('google.com')).one()

        ok_(res.stored >= now,
                "Stored time is now or close to now {0}:{1}".format(res.stored, now))

        res.url = "Somethingnew.com"
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
                'url': 'google.com',
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
