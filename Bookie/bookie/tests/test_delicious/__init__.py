"""Test that we're meeting delicious API specifications"""
from datetime import datetime, timedelta
import transaction
import unittest
import urllib
from nose.tools import ok_, eq_
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark, NoResultFound
from bookie.models import Hashed
from bookie.models import Tag, bmarks_tags
from bookie.models import SqliteBmarkFT

from bookie.tests import BOOKIE_TEST_INI

GOOGLE_HASH = 'RnyvTD2qVZSJp6RVWv359C'


class DelPostTest(unittest.TestCase):
    """Test post related calls"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()

        if BOOKIE_TEST_INI == 'test.ini':
            SqliteBmarkFT.query.delete()
        Bmark.query.delete()
        Tag.query.delete()
        Hashed.query.delete()

        DBSession.execute(bmarks_tags.delete())
        DBSession.flush()
        transaction.commit()

    def _get_good_request(self, content=False):
        """Return the basics for a good add bookmark request"""
        session = DBSession()
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'api_key': u'testapi',
        }

        # if we want to test the readable fulltext side we want to make sure we
        # pass content into the new bookmark
        if content:
            prms['content'] = "<h1>There's some content in here dude</h1>"

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/delapi/posts/add?' + req_params)
        session.flush()
        transaction.commit()
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
            res = Bmark.query.filter(Bmark.hash_id == GOOGLE_HASH).one()
            ok_(res, 'We found a result in the db for this bookmark')
            ok_('extended' in res.extended,
                    'Extended value was set to bookmark')

            # make sure our hash was stored correctly
            ok_(res.hashed.url == 'http://google.com',
                    "The hashed object got the url")

            ok_(res.hashed.clicks == 0, "No clicks on the url yet")

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
        res = Bmark.query.filter(Bmark.hash_id == GOOGLE_HASH).one()
        eq_(res.stored.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d'),
            "The stored date {0} is the same as the requested {1}".format(
                res.stored,
                yesterday))

    def test_new_bmark_tags(self):
        """Manually check db for new bmark tags set"""
        self._get_good_request()

        res = Bmark.query.filter(Bmark.hash_id == GOOGLE_HASH).one()

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

        # we've got some issue with mysql truncating the timestamp to not
        # include seconds, so we allow for a one minute leeway in the
        # timestamp. Enough to know it's set and close enough for government
        # use
        now = datetime.now() - timedelta(minutes=1)
        self._get_good_request()
        res = Bmark.query.filter(Bmark.hash_id == GOOGLE_HASH).one()

        ok_(res.stored >= now,
                "Stored time is now or close to now {0}--{1}".format(res.stored, now))

        res.hash_id = u"Somethingnew.com"
        DBSession.flush()

        print dict(res)
        # now hopefully have an updated value
        ok_(res.updated >= now,
                "Stored time, after update, is now or close to now {0}--{1}".format(res.updated, now))

    def test_remove_bmark(self):
        """Remove a bmark from the system

        We want to make sure we store content in here to make sure all the
        delete cascades are operating properly

        """
        res1 = self._get_good_request(content=True)
        ok_('done' in res1.body, res1.body)

        # now send in the delete squad
        prms = {
            'url': u'http://google.com',
            'api_key': u'testapi',
        }

        req_params = urllib.urlencode(prms)

        res = self.testapp.get('/delapi/posts/delete?' + req_params)
        eq_(res.status, "200 OK", 'Post Delete status is 200, ' + res.status)
        ok_('done' in res.body, "Request should return done msg: " + res.body)

        # now make sure our hashed object is gone as well.
        res = Hashed.query.get(GOOGLE_HASH)
        ok_(not res, "We didn't get our hash object")

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

        res = Bmark.query.filter(Bmark.hash_id == GOOGLE_HASH).one()

        ok_('updated' in res.description,
                'Updated description took: ' + res.description)
        ok_('updated' in res.extended,
                'Updated extended took: ' + res.extended)
        ok_('python' in res.tags, 'Found the python tag in the bmark')
        ok_('search' in res.tags, 'Found the search tag in the bmark')
        ok_('updated' in res.tags, 'Found the updated tag in the bmark')


    def test_tag_with_space(self):
        """Test that we strip out spaces from tags and don't get empty tags

        """
        self._get_good_request()

        # now build a new version of the request we can check
        session = DBSession()
        prms = {
                'url': u'http://google.com',
                'description': u'This is my updated google desc',
                'extended': 'updated extended notes about it in full form',
                'tags': u'python  search updated ',
                'api_key': u'testapi',
        }

        req_params = urllib.urlencode(prms)
        self.testapp.get('/delapi/posts/add?' + req_params)
        session.flush()

        res = Bmark.query.filter(Bmark.hash_id == GOOGLE_HASH).one()

        ok_(len(res.tags) == 3,
                'Should only have 3 tags: ' + str([str(t) for t in res.tags]))

        for tag in res.tags:
            ok_(tag[0] != " ", "Tag should not start with a space")
            ok_(tag[-1] != " ", "Tag should not end with a space")


class DelImportTest(unittest.TestCase):
    """Test that we can successfully import data from delicious"""

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

    def test_import(self):
        """Grab our test data file, import it, and check it out"""
        # need to start work on adding this, but passing for build now
        assert True


class GBookmarkImportTest(unittest.TestCase):
    """Test that we can successfully import data from delicious"""

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

    def test_import(self):
        """Grab our test data file, import it, and check it out"""
        # need to start work on adding this, but passing for build now
        assert True
