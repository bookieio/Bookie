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
