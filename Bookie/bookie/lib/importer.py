"""Importers for bookmarks"""
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from bookie.models import DBSession
from bookie.models import Bmark

class DelImporter(object):
    """Process a delicious html file"""

    def __init__(self, import_io):
        """Prepare to process"""
        self.file_handle = import_io

    @staticmethod
    def can_handle(file_io):
        """Check if this file is a google bookmarks format file

        In order to check the file we have to read it and check it's content
        type. 
        
        Google Bookmarks and Delicious both have the same content type, but
        they use different formats. We use the fact that Google Bookmarks 
        uses <h3> tags and Delicious does not in order to differentiate these
        two formats.
        """
        soup = BeautifulSoup(file_io)
        can_handle = False
        delicious_doctype = "DOCTYPE NETSCAPE-Bookmark-file-1"
        if soup.contents[0] == delicious_doctype and not soup.find('h3'):
            can_handle = True

        # make sure we reset the file_io object so that we can use it again
        file_io.seek(0)
        return can_handle


    def process(self):
        """Given a file, process it"""
        soup = BeautifulSoup(self.file_handle)

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


class GBookmarkImporter(object):
    """Process a Google Bookmark export html file"""

    def __init__(self, import_io):
        """Prepare to process the input file"""
        self.file_handle = import_io

    @staticmethod
    def can_handle(file_io):
        """Check if this file is a google bookmarks format file

        In order to check the file we have to read it and check it's content
        type

        Google Bookmarks and Delicious both have the same content type, but
        they use different formats. We use the fact that Google Bookmarks 
        uses <h3> tags and Delicious does not in order to differentiate these
        two formats.
        """
        soup = BeautifulSoup(file_io)
        can_handle = False
        gbookmark_doctype = "DOCTYPE NETSCAPE-Bookmark-file-1"
        if soup.contents[0] == gbookmark_doctype and soup.find('h3'):
            can_handle = True

        # make sure we reset the file_io object so that we can use it again
        file_io.seek(0)
        return can_handle

    def process(self):
        """Process an html google bookmarks export and import them into bookie
        The export format is a tag as a heading, with urls that have that tag
        under that heading. If a url has N tags, it will appear N times, once
        under each heading.
        """
        soup = BeautifulSoup(self.file_handle)
        if not soup.contents[0] == "DOCTYPE NETSCAPE-Bookmark-file-1":
            raise Exception("File is not a google bookmarks file")

        urls = dict() # url:url_metadata

        # we don't want to just import all the available urls, since each url 
        # occurs once per tag. loop through and aggregate the tags for each url
        for tag in soup.findAll('h3'): 
            links = tag.findNextSibling('dl').findAll("a")
            for link in links:
                url = link["href"]
                timestamp_added = float(link['add_date'])/1e6
                if url in urls:
                    urls[url]['tags'].append(tag.text) 
                else:
                    urls[url] = {
                        'description': link.text,
                        'tags': [tag.text] if tag.text != 'Unlabeled' else [],
                        'date_added': datetime.fromtimestamp(timestamp_added),
                    }

        # save the bookmark
        for url, metadata in urls.items():
            mark = Bmark(url,
                 desc=metadata['description'],
                 tags=" ".join(metadata['tags'])
            )

            mark.stored = metadata['date_added']

            session = DBSession()
            session.add(mark)
