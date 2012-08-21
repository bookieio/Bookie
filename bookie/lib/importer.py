"""Importers for bookmarks"""
import time
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from bookie.lib.urlhash import generate_hash
from bookie.models import BmarkMgr


IMPORTED = "importer"


class Importer(object):
    """The actual factory object we use for handling imports"""

    def __init__(self, import_io, username=None):
        """work on getting an importer instance"""
        self.file_handle = import_io
        self.username = username

        # we need to get our list of hashes to make sure we check for dupes
        self.hash_list = set([b[0] for b in BmarkMgr.hash_list(username=username)])

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

    def process(self, fulltext=None):
        """Meant to be implemented in subclasses"""
        raise NotImplementedError("Please implement this in your importer")

    def save_bookmark(self, url, desc, ext, tags, dt=None):
        """Save the bookmark to the db

        :param url: bookmark url
        :param desc: one line description
        :param ext: extended description/notes
        :param tags: The string of tags to store with this bmark
        :param mark: Instance of Bmark that we're storing to db

        """
        # we should make sure that this url isn't already bookmarked before
        # adding it...if the hash matches, you must skip!
        check_hash = generate_hash(url)
        if check_hash not in self.hash_list:
            BmarkMgr.store(url,
                           self.username,
                           desc,
                           ext,
                           tags,
                           dt=dt,
                           inserted_by=IMPORTED)

            # add this hash to the list so that we can skip dupes in the same
            # import set
            self.hash_list.add(check_hash)


class DelImporter(Importer):
    """Process a delicious html file"""

    @staticmethod
    def _is_delicious_format(soup, can_handle, delicious_doctype):
        """A check for if this import files is a delicious format compat file

        Very fragile currently, it makes sure the first line is the doctype.
        Any blank lines before it will cause it to fail

        """
        if soup.contents \
           and soup.contents[0] == delicious_doctype \
           and not soup.find('h3'):
            can_handle = True

        return can_handle

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
        can_handle = DelImporter._is_delicious_format(soup,
                                                   can_handle,
                                                   delicious_doctype)

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

            import_add_date = float(link['add_date'])

            if import_add_date > 9999999999:
                # Remove microseconds from the timestamp
                import_add_date = import_add_date / 1000
            add_date = datetime.fromtimestamp(import_add_date)

            self.save_bookmark(link['href'],
                               link.text,
                               extended,
                               " ".join(link['tags'].split(',')),
                               dt=add_date)


class GBookmarkImporter(Importer):
    """Process a Google Bookmark export html file"""

    @staticmethod
    def _is_google_format(soup, gbookmark_doctype, can_handle):
        """Verify that this import file is in the google export format

        Google only puts one tag at a time and needs to be looped through to
        get them all. See the sample files in the test_importer directory

        """
        if soup.contents \
           and soup.contents[0] == gbookmark_doctype \
           and soup.find('h3'):
            can_handle = True

        return can_handle

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
        can_handle = GBookmarkImporter._is_google_format(soup,
                                                         gbookmark_doctype,
                                                         can_handle)

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

        urls = dict()  # url:url_metadata

        # we don't want to just import all the available urls, since each url
        # occurs once per tag. loop through and aggregate the tags for each url
        for tag in soup.findAll('h3'):
            links = tag.findNextSibling('dl')

            if links is not None:
                links = links.findAll("a")

                for link in links:
                    url = link["href"]
                    tag_text = tag.text.replace(" ", "-")
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
                        if 'add_date' not in link:
                            link['add_date'] = time.time()

                        timestamp_added = float(link['add_date']) / 1e6

                        urls[url] = {
                            'description': link.text,
                            'tags': tags,
                            'extended': extended,
                            'date_added': datetime.fromtimestamp(
                                            timestamp_added),
                        }

        # save the bookmark
        for url, metadata in urls.items():
            self.save_bookmark(url,
                               metadata['description'],
                               metadata['extended'],
                               " ".join(metadata['tags']),
                               dt=metadata['date_added'])
