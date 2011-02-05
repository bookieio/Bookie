import os
import sys
import time
import getpass
import unittest

from pydelicious import DeliciousAPI, PyDeliciousException


class ApiSystemTest(unittest.TestCase):
    """Base class for API system tests.

    Derive API system tests from this baseclass.
    """

    def setUpApi(self, codec='latin-1'):
        "Setup API with custom encoding."
        global pwd, usr
        if not (usr or pwd):
            self.api = None;
        else:
            self.creds = usr, pwd
            self.api = DeliciousAPI(usr, pwd, codec)

            # should raise or return:
            update = self.api.posts_update()
            if not update:
                sys.exit("Cannot stat server, unknown error")

    def setUp(self):
        "Default setUp before each ApiSystemTest testcase"
        return self.setUpApi()

    def assertContains(self, container, object):
        self.failUnless(object in container, "%s not in %s" %(object, container))


class TestApiCalls(ApiSystemTest):

    """
    Test only wether calling stuff goes smoothly
    """

    def test_01_tags_get(self):
        self.assertEqual( type({}),
                type( self.api.tags_get() ) )

    def test_02_tags_rename(self):
        self.assertEqual( type({}),
                type( self.api.tags_rename("", "") ))

    def test_03_posts_update(self):
        self.assertEqual( type({}),
                type( self.api.posts_update() ))

    def test_04_posts_dates(self):
        self.assertEqual( type({}),
                type( self.api.posts_dates() ))

    def test_05_post_get(self):
        self.assertEqual( type({}),
                type( self.api.posts_get(tag="") ))

    def test_06_posts_recent(self):
        self.assertEqual( type({}),
                type( self.api.posts_recent() ))

    def test_07_posts_all(self):
        self.assertEqual( type({}),
                type( self.api.posts_all() ))

    def test_08_posts_add_remove(self):
        self.assertEqual( None,
                self.api.posts_add("http://sub.dom.tl/", "desc") )
        self.assertEqual( None,
                self.api.posts_delete("http://sub.dom.tl/") )


# used to store credentials
DLCS_TESTER = os.path.expanduser('~/.dlcs-tester')

def get_credentials():
    user, passwd = None, None

    if len(sys.argv)>1:
        _a = iter(sys.argv[1:])
        while _a:
            a = _a.next()
            if a[0] == '-':
                a = a.lstrip('-')

                if a.startswith('p'):
                    if '=' in a:
                        a, passwd = a.split('=')
                    # XXX: take passwd from cmdline?
                    else:
                        passwd = _a.next()


                elif a.startswith('u'):
                    if '=' in a:
                        a, user = a.split('=')
                    else:
                        user = _a.next()

    if not (user or passwd) and os.path.exists(DLCS_TESTER):
        user, passwd = open(DLCS_TESTER).read().strip().split(',')
        print "Loaded user %s from %s" % (user, DLCS_TESTER)

    if not user:
        print "Enter del.icio.us test account login (hit return to skip API tests)"
        user = raw_input("Username: ")

    if user:
        if not passwd:
            passwd = getpass.getpass("Password required for %s: " % user)

    if not os.path.exists(DLCS_TESTER):
        try:
            open(DLCS_TESTER, 'w+').write("%s,%s" % (user, passwd))
            os.chmod(DLCS_TESTER, 0600)
        except Exception, e:
            print >>sys.stderr,"Unable to save credentials to %s, error: %s" % (DLCS_TESTER, e)

    return user, passwd

# Get credentials, just once, save on module.
usr, pwd = get_credentials()

if __name__ == '__main__': unittest.main()
