"""Handle processing and setting web content into Readability/cleaned

"""
import httplib
import logging
import lxml
import socket
import urllib2

from BaseHTTPServer import BaseHTTPRequestHandler as HTTPH
from breadability.readable import Article
from urlparse import urlparse

LOG = logging.getLogger(__name__)


class DictObj(dict):
    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            return super(DictObj, self).__getattr__(name)


USER_AGENT = 'bookie / ({url})'.format(
    url="https://github.com/bookieio/bookie",
)


STATUS_CODES = DictObj({
    '1': 1,    # used for manual parsed
    '200': 200,
    '404': 404,
    '403': 403,
    '429': 429,   # wtf, 429 doesn't exist...

    # errors like 9's
    '900': 900,   # used for unparseable
    '901': 901,   # url is not parseable/usable
    '902': 902,   # socket.error during download
    '903': 903,   # httplib.IncompleteRead error
    '904': 904,   # lxml error about document is empty
    '905': 905,   # httplib.BadStatusLine
})

IMAGE_TYPES = DictObj({
    'png': 'image/png',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpg',
    'gif': 'image/gif',
})


class Readable(object):
    """Understand the base concept of making readable"""
    is_error = False
    content = None
    content_type = None
    headers = None
    status_message = None
    status = None
    url = None

    def error(self, code, msg):
        """This readable request was an error, assign it so"""
        self.status = code
        self.status_message = str(msg)

    def is_error(self):
        """Check if this is indeed an error or not"""
        if self.status not in [STATUS_CODES['200'], ]:
            return True
        else:
            return False

    def is_image(self):
        """Check if the current object is an image"""
        # we can only get this if we have headers
        LOG.debug('content type')
        LOG.debug(self.content_type)
        if (self.content_type is not None and
                self.content_type.lower() in IMAGE_TYPES.values()):
            return True
        else:
            return False

    def set_content(self, content, content_type=None):
        """assign the content and potentially content type header"""
        self.content = content
        if content_type:
            self.content_type = content_type


class ReadContent(object):
    """Handle some given content and parse the readable out of it"""

    @staticmethod
    def parse(content, content_type=None, url=None):
        """Handle the parsing out of the html content given"""
        read = Readable()
        document = Article(content.read(), url=url)

        if not document.readable:
            read.error(STATUS_CODES['900'], "Could not parse content.")
        else:
            read.set_content(document.readable,
                             content_type=content_type)
            read.status = STATUS_CODES['1']
        return read


class ReadUrl(object):
    """Fetch a url and read some content out of it"""

    @staticmethod
    def parse(url):
        """Fetch the given url and parse out a Readable Obj for the content"""
        read = Readable()

        if not isinstance(url, unicode):
            url = url.decode('utf-8')

        # first check if we have a special url with the #! content in it
        if u'#!' in url:
            # rewrite it with _escaped_fragment_=xxx
            # we should be doing with this some regex, but cheating for now
            idx = url.index(u'#')
            fragment = url[idx:]
            clean_url = u"{0}?_escaped_fragment_={1}".format(url[0:idx],
                                                             fragment)
        else:
            # we need to clean up the url first, we can't have any anchor tag
            # on the url or urllib2 gets cranky
            parsed = urlparse(url)

            # We cannot parse urls that aren't http, https, or ftp://
            if (parsed.scheme not in (u'http', u'https', u'ftp')):
                read.error(
                    STATUS_CODES['901'],
                    'Invalid url scheme for readable content')
                return read

            if parsed.query is not None and parsed.query != '':
                query = u'?'
            else:
                query = u''

            clean_url = u"{0}://{1}{2}{query}{3}".format(
                parsed[0],
                parsed[1],
                parsed[2],
                parsed[4],
                query=query)

        try:
            LOG.debug('Readable Parsed: ' + clean_url)
            request = urllib2.Request(clean_url.encode('utf-8'))
            request.add_header('User-Agent', USER_AGENT)
            opener = urllib2.build_opener()
            fh = opener.open(request)

            # if it works, then we default to a 200 request
            # it's ok, promise :)
            read.status = 200
            read.headers = fh.info()
            read.content_type = read.headers.gettype()

        except urllib2.HTTPError, exc:
            # for some reason getting a code 429 from a server
            if exc.code not in [429]:
                read.error(exc.code, HTTPH.responses[exc.code])
            else:
                read.error(exc.code, unicode(exc.code) + ': ' + clean_url)

        except httplib.InvalidURL, exc:
            read.error(STATUS_CODES['901'], str(exc))

        except urllib2.URLError, exc:
            read.error(STATUS_CODES['901'], str(exc))

        except httplib.BadStatusLine, exc:
            read.error(STATUS_CODES['905'], str(exc))

        except socket.error, exc:
            read.error(STATUS_CODES['902'], str(exc))

        LOG.debug('is error?')
        LOG.debug(read.status)

        # let's check to make sure we should be parsing this
        # for example: don't parse images
        if not read.is_error() and not read.is_image():
            try:
                document = Article(fh.read(), url=clean_url)
                if not document.readable:
                    read.error(STATUS_CODES['900'],
                               "Could not parse document.")
                else:
                    read.set_content(document.readable)

            except socket.error, exc:
                read.error(STATUS_CODES['902'], str(exc))
            except httplib.IncompleteRead, exc:
                read.error(STATUS_CODES['903'], str(exc))
            except lxml.etree.ParserError, exc:
                read.error(STATUS_CODES['904'], str(exc))

        return read
