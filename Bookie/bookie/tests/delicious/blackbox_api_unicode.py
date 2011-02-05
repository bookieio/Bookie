import unittest
import time
import blackbox_api
import pydelicious


class ApiUnicodeTest(blackbox_api.ApiSystemTest):
    def setUp(self):
        super(ApiUnicodeTest, self).setUpApi('utf8')
        self.post = (
            "http://code.google.com/pydelicious#ApiUnicodeTest",
            u"\u00b6 ApiUnicodeTest",
            u"This is a system test post\u2026",
            "tests urn:system t\xc3\xa1g t\xc3\xa0g t\xc3\xa5g".decode('utf8')
        )

    def test_1_add_post(self):
        a = self.api
        url, descr, extd, tags = self.post

        a.posts_add(url, descr, tags=tags, extended=extd, shared="yes")

    def test_2_check_posted(self):
        a = self.api
        url, descr, extd, tags = self.post

        p = a.posts_get(url=url)
        self.assertEqual( len(p['posts']), 1,
                "URL does not appear in collection after posts_add")

        self.failUnlessRaises(
            pydelicious.DeliciousItemExistsError,
            lambda: a.posts_add(url, descr, tags=tags, extended=extd, shared="yes") )

        post = p['posts'][0]
        self.assertContains(post, 'href')
        self.assertEqual(post['href'], url)
#        self.assertContains(post, 'shared')
#        self.assertEqual(post['shared'], 'yes')
        self.assertContains(post, 'tag')
        self.assertEqual(post['tag'], tags)
        self.assertContains(post, 'description')
        self.assertEqual(post['description'], descr)
        self.assertContains(post, 'extended')
        self.assertEqual(post['extended'], extd)


    def test_3_delete_post(self):
        a = self.api
        url, descr, extd, tags = self.post

        self.assertEqual( None, a.posts_delete(url) )

    def test_4_check_deleted(self):
        a = self.api
        url, descr, extd, tags = self.post

        p = a.posts_get(url=url)
        self.assertEqual(p['posts'], [],
                "Posted URL did not dissappear after posts_delete")


class ApiLatin1Test_2(ApiUnicodeTest):

    """Verify DeliciousAPI can write a post from latin1 environment.
    Data should be send/received as unicode.
    """

    def setUp(self):
        super(ApiLatin1Test_2, self).setUpApi('latin1')
        self.post = (
            "http://code.google.com/pydelicious#ApiLatin1Test-2",
            "\xb4 ApiLatin1Test-2".decode('latin1'),
            "This is a system test post",
            "tests urn:system \xa4 t\xe4g".decode('latin1')
        )

if __name__ == '__main__': unittest.main()
