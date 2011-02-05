# encoding: utf-8
import unittest


class CodecTest(unittest.TestCase):

    """this has nothing to do with pydelicious, but illustrates handling
    encodings.
    """

    t = {
        'latin1': {
            'ä': '\xe4'
        },
        'iso-8859-1' : {
            '¤': '\xA4',
            '¦': '\xA6',
            '¨': '\xA8',
            '´': '\xB4',
            '¸': '\xB8',
            '¼': '\xBC',
            '½': '\xBD',
            '¾': '\xBE'
        },
        'iso-8859-15': {
            '€': '\xA4',
            'Š': '\xA6',
            'š': '\xA8',
            'Ž': '\xB4',
            'ž': '\xB8',
            'Œ': '\xBC',
            'œ': '\xBD',
            'Ÿ': '\xBE'
        },
    }
    codecs = t.keys()

    def test_str_decode(self):
        for c in self.codecs:
            for k,v in self.t[c].items():

                ku = unicode(k, 'utf-8')
                self.assertEqual(ku, v.decode(c))
                self.assertEqual(v.decode(c),
                    unicode(v, c))

    def test_unicode_encode(self):
        for c in self.codecs:
            for k,v in self.t[c].items():

                ku = unicode(k, 'utf-8')
                self.assertEqual(ku.encode(c), v)

    def test_unicode(self):
        for c in self.codecs:
            for k,v in self.t[c].items():

                ku = unicode(k, 'utf-8')
                vu = unicode(v, c)
                self.assertEqual(ku, vu)


if __name__ == '__main__': unittest.main()
