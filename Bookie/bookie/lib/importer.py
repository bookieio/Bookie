"""Importers for bookmarks"""
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from bookie.models import DBSession
from bookie.models import Bmark


class Importer(object):
    """The actual factory object we use for handling imports"""

    def __init__(self, import_io):
        """work on getting an importer instance"""
        self.file_handle = import_io

    def __new__(cls, *args, **kwargs):
        """Overriding new we return a subclass based on the file content"""
        if DelImporter.can_handle(args[0]):
            return super(Importer, cls).__new__(DelImporter)

        if GBookmarkImporter.can_handle(args[0]):
            return super(Importer, cls).__new__(GBookmarkImporter)

        return super(Importer, cls).__new__(Importer)

    @staticmethod
    def can_handle(file_io):
        """This is meant to be implemented in subclasses"""
        raise NotImplementedError("Please implement this in your importer")

    def process(self):
        """Meant to be implemented in subclasses"""
        raise NotImplementedError("Please implement this in your importer")


class DelImporter(Importer):
    """Process a delicious html file"""

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
        delicious_doctype = "DOCTYPE NETSCAPE-Bookmark-file-1"

        soup = BeautifulSoup(file_io)
        can_handle = False
        if soup.contents and soup.contents[0] == delicious_doctype and not soup.find('h3'):
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


class GBookmarkImporter(Importer):
    """Process a Google Bookmark export html file"""

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
        if soup.contents and soup.contents[0] == gbookmark_doctype and soup.find('h3'):
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
                tag_text = tag.text.replace(" ","-")
                if url in urls:
                    urls[url]['tags'].append(tag_text)
                else:
                    tags = [tag_text] if tag_text != 'Unlabeled' else []

                    # get extended description
                    has_extended = (link.parent.nextSibling and
                            link.parent.nextSibling.name == 'dd')
                    if has_extended:
                        extended = link.parent.nextSibling.text
                    else:
                        extended = ""

                    # date the site was bookmarked
                    timestamp_added = float(link['add_date'])/1e6

                    urls[url] = {
                        'description': link.text,
                        'tags': tags,
                        'extended': extended,
                        'date_added': datetime.fromtimestamp(timestamp_added),
                    }

        # save the bookmark
        for url, metadata in urls.items():
            mark = Bmark(url,
                 desc=metadata['description'],
                 tags=" ".join(metadata['tags']),
                 ext=metadata['extended']
            )

            mark.stored = metadata['date_added']

            session = DBSession()
            session.add(mark)
