"""Unittests for pydelicious module.
"""
import sys, os
import unittest
import urllib
import urllib2
import pydelicious
import time
from StringIO import StringIO

test_data = {
    # old rss feeds
    'http://del.icio.us/rss/': 'var/rss.xml',
    'http://del.icio.us/rss/popular/': 'var/rss_popular.xml',
    'http://del.icio.us/rss/tag/python': 'var/rss_tag_python.xml',
    'http://del.icio.us/rss/pydelicious': 'var/rss_pydelicious.xml',
    'http://del.icio.us/rss/url/efbfb246d886393d48065551434dab54': 'var/rss_url.xml',

    # v2 feeds
    'http://feeds.delicious.com/v2/json': 'var/feed_v2.json',
    'http://feeds.delicious.com/v2/rss': 'var/feed_v2.rss',
    'http://feeds.delicious.com/v2/json/recent': 'var/feed_v2_recent.json',
    'http://feeds.delicious.com/v2/rss/recent': 'var/feed_v2_recent.rss.xml',

}
def fetch_file(url, fn):
    data = urllib2.urlopen(url).read()
    if os.path.exists(fn):
        acted = 'Overwritten'
    else:
        acted = 'New'
    open(fn, 'w+').write(data)
    print "%s file %s for <%s>" % (acted, fn, url)

def http_request_dummy(url, user_agent=None, retry=0, opener=None):
    if url in test_data:
        fn = test_data[url]
        if not os.path.isfile(fn): 
            fetch_file(url, fn)
        return open(fn)

    else:
        return StringIO(url)

# Turn of all HTTP fetching in pydelicious,
# don't do http requests but return pre-def data
# See blackbox tests if you want to test for real
pydelicious.http_request = http_request_dummy


def api_request_dummy(path, params='', user='', passwd='', opener=None):

    """Instead of mimicking the server responses this will return a tuple
    including the url.
    """

    if params:
        url = "%s/%s?%s" % (pydelicious.DLCS_API, path, urllib.urlencode(params))
    else:
        url = "%s/%s" % (pydelicious.DLCS_API, path)
    return url, user, passwd

def parser_dummy(data, split_tags=False):
    return {'not-parsed':data}



class PyDeliciousTester(unittest.TestCase):

    def assertContains(self, container, object):
        self.failUnless(object in container, "%s not in %s" %(object, container))


class TestWaiter(PyDeliciousTester):

    def testwait1(self):
        wt = pydelicious.DLCS_WAIT_TIME

        # First call, no wait needed
        t = time.time()
        pydelicious.Waiter()
        waited = round(time.time() - t, 1)
        self.assert_(waited < wt,
                "unneeded wait of %s" % (waited,))

        # Some values between full wait intervals
        for w in .4, .7, 1.5:
            time.sleep(w)
            t = time.time()
            pydelicious.Waiter()
            waited = round(time.time() - t, 1)
            self.assert_(waited <= pydelicious.DLCS_WAIT_TIME,
                    "unneeded wait of %s (not %s)" % (w,
                        pydelicious.DLCS_WAIT_TIME-w))

        # Some more regular intervals
        t = time.time()
        for i in range(0, 2):
            pydelicious.Waiter()
            waited = time.time() - t
            self.assert_(waited >= i*wt,
                    "needed wait of %s, not %s" % (i*wt, waited,))


class TestGetrss(PyDeliciousTester):

    "test old RSS feed parsing"

#    def test_dlcs_rss_request(self):
#        f = pydelicious.dlcs_rss_request
#        pass

    def test_getrss(self):
        self.assert_(pydelicious.feedparser, "feedparser required for this test")
        p = pydelicious.getrss
        self.assertEqual(
                type(p()), type([]) )
        self.assertEqual(
                type(p(popular=1)), type([]) )
        self.assert_(
                type(p(tag="python")), type([]) )
        self.assert_(
                type(p(user="pydelicious")), type([]) )
        self.assertEqual(
                type(p(url="http://deliciouspython.python-hosting.com/")),
                type([]) )


class TestFeeds(PyDeliciousTester):

    """
    TODO: implement json/rss parsing
    """

    def test_getfeed(self):
        f = pydelicious.getfeed
        data = f('')
        self.assertEqual( data[:2]+data[-2:], '[{}]' )

        if pydelicious.feedparser:
            pass # TODO
        else:
            self.assert_( f('', format='rss').startswith('<?xml version="1.0" encoding="UTF-8"?>') )

#        print f('', format='json')
#        print f('recent')
#        print f('recent', format='rss')


class TestBug(PyDeliciousTester):

    def testBug2(self):
        '''testbug2: via deepak.jois@gmail.com
        missing "" in {"user":user}'''
        self.assert_(pydelicious.feedparser, "feedparser required for this test")
        self.assertEqual(
            type(pydelicious.getrss(tag="read",user="deepakjois")),
            type([]))


class DeliciousApiUnitTest(PyDeliciousTester):

    """Simply tests wether DeliciousAPI.request(`path`, `args`) results in the same URL as
    DeliciousAPI.`path`(`args`)
    """

    def setUp(self):
        self.api_utf8 = pydelicious.DeliciousAPI('testUser', 'testPwd',
            'utf-8', api_request=api_request_dummy, xml_parser=parser_dummy)

        self.api_latin1 = pydelicious.DeliciousAPI('testUser', 'testPwd',
            'latin-1', api_request=api_request_dummy, xml_parser=parser_dummy)

    def test_param_encoding(self):
        a = self.api_utf8
        params = {
            'foo': '\xe2\x98\x85',
            'bar': '\xc3\xa4'
        }
        params = a._encode_params(params, a.codec)
        self.assert_('foo=%E2%98%85' in urllib.urlencode(params))
        self.assert_('bar=%C3%A4' in urllib.urlencode(params))

        a = self.api_latin1
        params = {
            'bar': '\xe4',
            'baz': '\xa4'
        }
        params = a._encode_params(params, a.codec)
        self.assert_('bar=%C3%A4' in urllib.urlencode(params))
        self.assert_('baz=%C2%A4' in urllib.urlencode(params))

    def test_fetch_vs_methods(self):
        a = self.api_utf8

        self.assertEqual(a.request('tags/get'), a.tags_get())
        self.assertEqual(a.request('tags/rename', old='tag1', new='tag2'), a.tags_rename('tag1', 'tag2'))

        self.assertEqual(a.request('posts/update'), a.posts_update())
        self.assertEqual(a.request('posts/dates'), a.posts_dates())
        self.assertEqual(a.request('posts/get', meta='yes'), a.posts_get())
        self.assertEqual(a.request('posts/get', meta=True), a.posts_get())
        self.assertEqual(a.request('posts/recent'), a.posts_recent())
        self.assertEqual(a.request('posts/all', meta=True), a.posts_all())
        self.assertEqual(a.request('posts/add', url='url1', description='descr1', replace='no', shared='no'), a.posts_add('url1', 'descr1', replace='no', shared='no'))
        self.assertEqual(a.request('posts/delete', url='url1'), a.posts_delete('url1'))

        self.assertEqual(a.request('tags/bundles/all'), a.bundles_all())
        self.assertEqual(a.request('tags/bundles/set', bundle='bundle1', tags='tag1 tag2'), a.bundles_set('bundle1', 'tag1 tag2'))
        self.assertEqual(a.request('tags/bundles/delete', bundle='bundle1'), a.bundles_delete('bundle1'))

    def test_fetch_raw_vs_methods(self):
        a = self.api_utf8

        self.assertEqual(a.request_raw('tags/get'), a.tags_get(_raw=True))
        self.assertEqual(a.request_raw('tags/rename', old='tag1', new='tag2'), a.tags_rename('tag1', 'tag2', _raw=True))

        self.assertEqual(a.request_raw('posts/update'), a.posts_update(_raw=True))
        self.assertEqual(a.request_raw('posts/dates'), a.posts_dates(_raw=True))
        self.assertEqual(a.request_raw('posts/get', meta=True), a.posts_get(_raw=True))
        self.assertEqual(a.request_raw('posts/get', meta='yes'), a.posts_get(_raw=True))
        self.assertEqual(a.request_raw('posts/recent'), a.posts_recent(_raw=True))
        self.assertEqual(a.request_raw('posts/all', meta=True), a.posts_all(_raw=True))
        self.assertEqual(a.request_raw('posts/add', url='url1', description='descr1', replace='no', shared='no'), a.posts_add('url1', 'descr1', replace='no', shared='no', _raw=True))
        self.assertEqual(a.request_raw('posts/delete', url='url1'), a.posts_delete('url1', _raw=True))

        self.assertEqual(a.request_raw('tags/bundles/all'), a.bundles_all(_raw=True))
        self.assertEqual(a.request_raw('tags/bundles/set', bundle='bundle1', tags='tag1 tag2'), a.bundles_set('bundle1', 'tag1 tag2', _raw=True))
        self.assertEqual(a.request_raw('tags/bundles/delete', bundle='bundle1'), a.bundles_delete('bundle1', _raw=True))

class DeliciousErrorTest(PyDeliciousTester):

    def test_raiseFor(self):
        self.assertRaises(
            pydelicious.DeliciousItemExistsError,
            pydelicious.DeliciousError.raiseFor, 'item already exists',
                'path/add', **{'url':'urn:system'});
        self.assertRaises(
            pydelicious.DeliciousError,
            pydelicious.DeliciousError.raiseFor, 'other error', 'path/get'
            );


__testcases__ = (TestGetrss, TestBug, TestFeeds, DeliciousApiUnitTest, DeliciousErrorTest)#TestWaiter, )

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == 'refresh_test_data':
        for url, fn in test_data.items():
            if os.path.exists(fn):
                fetch_file(url, fn)

    else:
        unittest.main()
