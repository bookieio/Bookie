"""Importers for bookmarks"""
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from bookie.models import DBSession
from bookie.models import Bmark

class DelImporter(object):
    """Process a delicious html file"""

    def __init__(self, import_io):
        """Prepare to process"""
        self.io = import_io

    @staticmethod
    def can_handle(file_io):
        """Check if this file is a google bookmarks format file

        In order to check the file we have to read it and check it's content
        type
        """
        soup = BeautifulSoup(bmark_file)
        can_handle = false
        if soup.contents[0] == "DOCTYPE NETSCAPE-Bookmark-file-1":
            can_handle = True

        # make sure we reset the file_io object so that we can use it again
        file_io.seek(0)
        return can_handle


    def process(self):
        """Given a file, process it"""
        soup = BeautifulSoup(self.io)

        for tag in soup.findAll('dt'):
            # if we have a dd as next sibling, get it's content
            if tag.nextSibling and tag.nextSibling.name == 'dd':
                extended = tag.nextSibling.text
            else:
                extended = ""

            link = tag.a

            add_date = datetime.fromtimestamp(float(link['add_date']))
            mark = Bmark(link['href'],
                 desc=link.text,
                 ext=extended,
                 tags=" ".join(link['tags'].split(',')),
            )

            add_date = datetime.fromtimestamp(float(link['add_date']))
            mark.stored = add_date

            session = DBSession()
            session.add(mark)

class GoogleImporter(object):
    """Process the result of a google bookmarks export"""

    def __init__(self, import_io):
        """Prepare to process the input file"""
        self.io = import_io

    @staticmethod
    def can_handle(file_io):
        """Check if this file is a google bookmarks format file

        In order to check the file we have to read it and check it's content
        type
        """
        soup = BeautifulSoup(bmark_file)
        can_handle = false
        if soup.contents[0] == "DOCTYPE NETSCAPE-Bookmark-file-1":
            can_handle = True

        # make sure we reset the file_io object so that we can use it again
        file_io.seek(0)
        return can_handle

    def process(self):
        """Process the bookmarks in the google export"""
        soup = BeautifulSoup(bmark_file)

        # @todo, this is actually the same for both of the types of bookmark
        # importers

