"""Handle processing and setting web content into Readability/cleaned

"""
import logging
import urllib2


from BaseHTTPServer import BaseHTTPRequestHandler as HTTPH
from decruft import Document
from decruft import page_parser

LOG = logging.getLogger(__name__)

class DictObj(dict):
    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            return super(DictObj, self).__getattr__(name)

STATUS_CODES = DictObj({
    '001': 001,    # used for unparseable
    '200': 200,
    '404': 404,
    '403': 403,
})

IMAGE_TYPES = DictObj({
    'png': 'image/png',
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
        self.status_message = msg

    def is_error(self):
        """Check if this is indeed an error or not"""
        if self.status not in [STATUS_CODES['200'], ]:
            return True
        else:
            return False

    def is_image(self):
        """Check if the current object is an image"""
        if self.content_type in IMAGE_TYPES:
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


class ReadUrl(object):
    """Fetch a url and read some content out of it"""


    @staticmethod
    def parse(url):
        """Fetch the given url and parse out a Readable Obj for the content"""
        read = Readable()

        try:
            fh = urllib2.urlopen(url)

            # if it works, then we default to a 200 request
            # it's ok, promise :)
            read.status = 200
            read.headers = fh.info()

        except urllib2.HTTPError, exc:
            read.error(exc.code, HTTPH.responses[exc.code])

        LOG.debug('is error')
        LOG.debug(read.status)
        LOG.debug(read.is_error())
        # let's check to make sure we should be parsing this
        # for example: don't parse images
        if not read.is_error() and not read.is_image():
            try:
                read.set_content(Document(fh.read()).summary(),
                                 content_type=read.headers.gettype(),)

            except page_parser.Unparseable, exc:
                read.error(STATUS_CODES['001'], str(exc))

        return read

