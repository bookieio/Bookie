# encoding: latin1
import unittest
import blackbox_api_unicode


class ApiLatin1Test(blackbox_api_unicode.ApiUnicodeTest):

    def setUp(self):
        super(ApiLatin1Test, self).setUpApi('latin1')
        self.post = (
            "http://code.google.com/pydelicious#ApiLatin1Test",
            u"\xb4 ApiLatin1Test-2",
            "This is a system test post",
            u"tests urn:system \xa4 t\xe4g"
        )


if __name__ == '__main__': unittest.main()
