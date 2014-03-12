"""Importers for bookmarks"""
import json
import os
import random
import string
import time
import transaction
from datetime import datetime
from dateutil import parser as dateparser
from BeautifulSoup import BeautifulSoup
from lxml import etree
from lxml.etree import XMLSyntaxError

from bookie.lib.urlhash import generate_hash
from bookie.models import (
    BmarkMgr,
    DBSession,
    InvalidBookmark,
)


IMPORTED = u"importer"
COMMIT_SIZE = 25


def store_import_file(storage_dir, username, files):
    # save the file off to the temp storage
    out_dir = "{storage_dir}/{randdir}".format(
        storage_dir=storage_dir,
        randdir=random.choice(string.letters),
    )

    # make sure the directory exists
    # we create it with parents as well just in case
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    out_fname = "{0}/{1}.{2}".format(
        out_dir, username, files.filename)
    out = open(out_fname, 'w')
    out.write(files.file.read())
    out.close()

    return out_fname


class Importer(object):
    """The actual factory object we use for handling imports"""

    def __init__(self, import_io, username=None):
        """work on getting an importer instance"""
        self.file_handle = import_io
        self.username = username

        # we need to get our list of hashes to make sure we check for dupes
        self.hash_list = set([b[0] for b in
                             BmarkMgr.hash_list(username=username)])

    def __new__(cls, *args, **kwargs):
        """Overriding new we return a subclass based on the file content"""
        if DelImporter.can_handle(args[0]):
            return super(Importer, cls).__new__(DelImporter)

        if DelXMLImporter.can_handle(args[0]):
            return super(Importer, cls).__new__(DelXMLImporter)

        if GBookmarkImporter.can_handle(args[0]):
            return super(Importer, cls).__new__(GBookmarkImporter)

        if FBookmarkImporter.can_handle(args[0]):
            return super(Importer, cls).__new__(FBookmarkImporter)

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
        # If a bookmark has the tag "private" then we ignore it to prevent
        # leaking user data.
        if tags and 'private' in tags.lower().split(' '):
            return None

        check_hash = generate_hash(url)

        # We should make sure that this url isn't already bookmarked before
        # adding it...if the hash matches, you must skip!
        if check_hash not in self.hash_list:
            bmark = BmarkMgr.store(
                url,
                self.username,
                desc,
                ext,
                tags,
                dt=dt,
                inserted_by=IMPORTED
            )

            # Add this hash to the list so that we can skip dupes in the
            # same import set.
            self.hash_list.add(check_hash)
            return bmark

        # If we don't store a bookmark then just return None back to the
        # importer.
        return None


class DelImporter(Importer):
    """Process a delicious html file"""

    @staticmethod
    def _is_delicious_format(soup, can_handle, delicious_doctype):
        """A check for if this import files is a delicious format compat file

        Very fragile currently, it makes sure the first line is the doctype.
        Any blank lines before it will cause it to fail

        """
        if (soup.contents and
                soup.contents[0] == delicious_doctype and
                not soup.find('h3')):
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
        delicious_doctype = u'DOCTYPE NETSCAPE-Bookmark-file-1'

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
        count = 0

        ids = []
        for tag in soup.findAll('dt'):
            if 'javascript:' in str(tag):
                continue

            # if we have a dd as next sibling, get it's content
            if tag.nextSibling and tag.nextSibling.name == 'dd':
                extended = tag.nextSibling.text
            else:
                extended = u""

            link = tag.a

            # Skip any bookmarks with an attribute of PRIVATE.
            if link.has_key('PRIVATE'):
                continue

            import_add_date = float(link['add_date'])

            if import_add_date > 9999999999:
                # Remove microseconds from the timestamp
                import_add_date = import_add_date / 1000
            add_date = datetime.fromtimestamp(import_add_date)

            try:
                bmark = self.save_bookmark(
                    unicode(link['href']),
                    unicode(link.text),
                    unicode(extended),
                    u" ".join(unicode(link.get('tags', '')).split(u',')),
                    dt=add_date)
                count = count + 1
                DBSession.flush()
            except InvalidBookmark:
                bmark = None

            if bmark:
                ids.append(bmark.bid)

            if count % COMMIT_SIZE == 0:
                transaction.commit()

        # Commit any that are left since the last commit performed.
        transaction.commit()

        from bookie.bcelery import tasks
        # For each bookmark in this set that we saved, sign up to
        # fetch its content.
        for bid in ids:
            tasks.fetch_bmark_content.delay(bid)

        # Start a new transaction for the next grouping.
        transaction.begin()


class DelXMLImporter(Importer):
    """Process a delicious xml export file"""

    @staticmethod
    def _is_delicious_format(parsed, can_handle):
        """A check for if this import files is a delicious xml format compat

        The root xml element will be 'posts' if this is the case.

        """
        if parsed.docinfo and parsed.docinfo.root_name == 'posts':
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

        try:
            file_io.seek(0)
            parsed = etree.parse(file_io)
        except XMLSyntaxError:
            # IF etree can't parse it, it's not our file.
            return False
        can_handle = False
        can_handle = DelXMLImporter._is_delicious_format(parsed,
                                                         can_handle)

        # make sure we reset the file_io object so that we can use it again
        return can_handle

    def process(self):
        """Given a file, process it"""
        if self.file_handle.closed:
            self.file_handle = open(self.file_handle.name)

        self.file_handle.seek(0)
        parsed = etree.parse(self.file_handle)
        count = 0

        ids = []
        for post in parsed.findall('post'):
            if 'javascript:' in post.get('href'):
                continue

            add_date = dateparser.parse(post.get('time'))

            try:
                bmark = self.save_bookmark(
                    unicode(post.get('href')),
                    unicode(post.get('description')),
                    unicode(post.get('extended')),
                    unicode(post.get('tag')),
                    dt=add_date)
                count = count + 1
                if bmark:
                    bmark.stored = bmark.stored.replace(tzinfo=None)
                    DBSession.flush()
            except InvalidBookmark:
                bmark = None

            if bmark:
                ids.append(bmark.bid)

            if count % COMMIT_SIZE == 0:
                transaction.commit()

        # Commit any that are left since the last commit performed.
        transaction.commit()

        from bookie.bcelery import tasks
        # For each bookmark in this set that we saved, sign up to
        # fetch its content.
        for bid in ids:
            tasks.fetch_bmark_content.delay(bid)

        # Start a new transaction for the next grouping.
        transaction.begin()


class GBookmarkImporter(Importer):
    """Process a Google Bookmark export html file"""

    @staticmethod
    def _is_google_format(soup, gbookmark_doctype, can_handle):
        """Verify that this import file is in the google export format

        Google only puts one tag at a time and needs to be looped through to
        get them all. See the sample files in the test_importer directory

        """
        if (soup.contents and
                soup.contents[0] == gbookmark_doctype and
                soup.find('h3')):
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
        if (file_io.closed):
            file_io = open(file_io.name)
        file_io.seek(0)
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
        count = 0
        if (self.file_handle.closed):
            self.file_handle = open(self.file_handle.name)
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
                    if url.startswith('javascript:'):
                        continue
                    tag_text = tag.text.replace(" ", "-")
                    if url in urls:
                        urls[url]['tags'].append(tag_text)
                    else:
                        tags = [tag_text] if tag_text != 'Unlabeled' else []

                        # get extended description
                        has_extended = (
                            link.parent.nextSibling and
                            link.parent.nextSibling.name == 'dd')
                        if has_extended:
                            extended = link.parent.nextSibling.text
                        else:
                            extended = ""

                        # Must use has_key here due to the link coming from
                        # the parser and it's not a true dict.
                        if link.has_key('add_date'):
                            if int(link['add_date']) < 9999999999:
                                timestamp_added = int(link['add_date'])
                            else:
                                timestamp_added = float(link['add_date']) / 1e6
                        else:
                            link['add_date'] = time.time()

                        urls[url] = {
                            'description': link.text,
                            'tags': tags,
                            'extended': extended,
                            'date_added': datetime.fromtimestamp(
                                timestamp_added),
                        }

        # save the bookmarks
        ids = []
        for url, metadata in urls.items():
            try:
                bmark = self.save_bookmark(
                    unicode(url),
                    unicode(metadata['description']),
                    unicode(metadata['extended']),
                    u" ".join(metadata['tags']),
                    dt=metadata['date_added'])
                DBSession.flush()
            except InvalidBookmark:
                bmark = None
            if bmark:
                ids.append(bmark.bid)
            if count % COMMIT_SIZE == 0:
                transaction.commit()
                # Start a new transaction for the next grouping.
                transaction.begin()

        # Commit any that are left since the last commit performed.
        transaction.commit()

        from bookie.bcelery import tasks
        # For each bookmark in this set that we saved, sign up to
        # fetch its content.
        for bid in ids:
            tasks.fetch_bmark_content.delay(bid)


class FBookmarkImporter(Importer):
    """Process a FireFox backup export json file"""
    MOZ_CONTAINER = "text/x-moz-place-container"

    @staticmethod
    def _is_firefox_format(json, can_handle):
        """Verify that this import file is in the firefox backup
        export format

        Firefox json file has a variable "type" which is equal to
        "text/x-moz-place-container"
        """
        if json['type'] == FBookmarkImporter.MOZ_CONTAINER:
            can_handle = True

        return can_handle

    @staticmethod
    def can_handle(file_io):
        """Check if this file is a Firefox bookmarks format file

        In order to check the file we have to read it and check it's content
        has a variable "type" which is equal to "text/x-moz-place-container"
        """
        if (file_io.closed):
            file_io = open(file_io.name)
        file_io.seek(0)
        can_handle = False
        try:
            backup_json = json.load(file_io)
        except:
            file_io.seek(0)
            return can_handle

        can_handle = FBookmarkImporter._is_firefox_format(backup_json,
                                                          can_handle)

        # make sure we reset the file_io object so that we can use it again
        file_io.seek(0)
        return can_handle

    def bmap_add(self, bmark, bmap):
        if bmark["uri"] not in bmap:
            bmap[bmark["uri"]] = bmark

    def process(self):
        """Process an json firefox bookmarks export and import them into bookie
        """
        MOZ_PLACE = "text/x-moz-place"
        UNWANTED_SCHEME = ("data", "place", "javascript")

        count = 0
        if (self.file_handle.closed):
            self.file_handle = open(self.file_handle.name)

        content = self.file_handle.read().decode("UTF-8")
        # HACK: Firefox' JSON writer leaves a trailing comma
        # HACK: at the end of the array, which no parser accepts
        if content.endswith(u"}]},]}"):
            content = content[:-6] + u"}]}]}"
        root = json.loads(content)

        # make a dictionary of unique bookmarks
        bmap = {}

        # check if uri of child starts with "data", "place", "javascript"
        def is_good(child):
            return not child["uri"].split(":", 1)[0] in UNWANTED_SCHEME

        # find toplevel subfolders and tag folders
        folders = []
        tagfolders = []
        for child in root["children"]:
            if child.get("root") == "tagsFolder":
                tagfolders.extend(child["children"])
            elif child.get("root"):
                folders.append(child)

        # visit all subfolders recursively
        visited = set()
        while folders:
            next = folders.pop()
            if next["id"] in visited:
                continue
            for child in next["children"]:
                if child["type"] == self.MOZ_CONTAINER:
                    folders.append(child)
                    tagfolders.append(child)
                elif child["type"] == MOZ_PLACE and \
                        child.get("uri") and \
                        is_good(child):
                    self.bmap_add(child, bmap)
            visited.add(next["id"])

        # visit all tag folders
        for tag in tagfolders:
            for bmark in tag["children"]:
                if bmark["type"] == MOZ_PLACE and \
                        bmark.get("uri") and \
                        is_good(bmark):
                    self.bmap_add(bmark, bmap)
                    if not "tags" in bmap[bmark["uri"]]:
                        bmap[bmark["uri"]]["tags"] = []
                    bmap[bmark["uri"]]["tags"].append(
                        tag["title"].replace(" ", "-"))

        # save the bookmarks
        # annos has the information about the url like name, flags, expires,
        # value, type etc
        ids = []
        for url, metadata in bmap.items():
            if metadata.get('annos') is not None:
                if metadata.get('annos')[0].get('value') is None:
                    metadata['annos'][0]['value'] = ''
            else:
                metadata['annos'] = [{}]
                metadata['annos'][0]['value'] = ''
            if metadata.get('tags') is None:
                metadata['tags'] = ''
            try:
                bookmark = self.save_bookmark(
                    unicode(url),
                    unicode(metadata['title']),
                    unicode(metadata['annos'][0]['value']),
                    u" ".join(metadata['tags']),
                    dt=datetime.fromtimestamp(
                        metadata['dateAdded']/1e6))
                DBSession.flush()
            except InvalidBookmark:
                bookmark = None
            if bookmark:
                ids.append(bookmark.bid)
            if count % COMMIT_SIZE == 0:
                transaction.commit()
                # Start a new transaction for the next grouping.
                transaction.begin()

        # Commit any that are left since the last commit performed.
        transaction.commit()

        from bookie.bcelery import tasks
        # For each bookmark in this set that we saved, sign up to
        # fetch its content.
        for bid in ids:
            tasks.fetch_bmark_content.delay(bid)
