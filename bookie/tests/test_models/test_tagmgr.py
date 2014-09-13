"""Test the basics including the bmark and tags"""

from bookie.models import (
    DBSession,
    Tag,
    TagMgr,
)
from bookie.models.auth import User

from bookie.tests import gen_random_word
from bookie.tests import TestDBBase
from bookie.tests.factory import (
    make_tag,
    make_bookmark,
)


class TestTagMgrStats(TestDBBase):
    """Handle some TagMgr stats checks"""

    def test_total_ct(self):
        """Verify that our total count method is working"""
        ct = 5
        for i in range(ct):
            t = Tag(gen_random_word(10))
            DBSession.add(t)

        ct = TagMgr.count()
        self.assertEqual(5, ct, 'We should have a total of 5: ' + str(ct))

    def test_basic_complete_same_user(self):
        """Tags should provide completion options."""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)

        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)
        bmark_tags = u" ".join(tag_names)
        bmark_url = u'http://bmark.us'
        bmark_desc = u'This is a test bookmark'
        bmark_ext = u'Some extended notes'

        # Store the bookmark.
        bmark = make_bookmark(is_private=True)
        bmark.url = bmark_url
        bmark.username = user.username
        bmark.description = bmark_desc
        bmark.extended = bmark_ext
        bmark.tags = TagMgr.from_string(bmark_tags)
        bmark.is_private = False
        DBSession.add(bmark)

        test_str = tags[0].name[0:2]
        suggestions = TagMgr.complete(test_str, username=user.username,
                                      requested_by=user.username)
        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")

    def test_basic_complete_same_user_accounts_for_privacy(self):
        """Tags should provide completion options."""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)

        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)
        bmark_tags = u" ".join(tag_names)
        bmark_url = u'http://bmark.us'
        bmark_desc = u'This is a test bookmark'
        bmark_ext = u'Some extended notes'

        # Store the bookmark.
        bmark = make_bookmark(is_private=True)
        bmark.url = bmark_url
        bmark.username = user.username
        bmark.description = bmark_desc
        bmark.extended = bmark_ext
        bmark.tags = TagMgr.from_string(bmark_tags)
        DBSession.add(bmark)

        test_str = tags[0].name[0:2]
        suggestions = TagMgr.complete(test_str, username=user.username,
                                      requested_by=user.username)
        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")

    def test_basic_complete_diff_user(self):
        """Tags should provide completion options."""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)

        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)
        bmark_tags = u" ".join(tag_names)
        bmark_url = u'http://bmark.us'
        bmark_desc = u'This is a test bookmark'
        bmark_ext = u'Some extended notes'

        # Store the bookmark.
        bmark = make_bookmark(is_private=True)
        bmark.url = bmark_url
        bmark.username = user.username
        bmark.description = bmark_desc
        bmark.extended = bmark_ext
        bmark.tags = TagMgr.from_string(bmark_tags)
        bmark.is_private = False
        DBSession.add(bmark)

        test_str = tags[0].name[0:2]
        suggestions = TagMgr.complete(test_str, username=user.username,
                                      requested_by=gen_random_word(10))
        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")

        # Also check when username is None.
        suggestions = TagMgr.complete(test_str, username=None)
        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")

    def test_basic_complete_diff_user_accounts_for_privacy(self):
        """Tags should not provide completion options."""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)

        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)
        bmark_tags = u" ".join(tag_names)
        bmark_url = u'http://bmark.us'
        bmark_desc = u'This is a test bookmark'
        bmark_ext = u'Some extended notes'

        # Store the bookmark.
        bmark = make_bookmark(is_private=True)
        bmark.url = bmark_url
        bmark.username = user.username
        bmark.description = bmark_desc
        bmark.extended = bmark_ext
        bmark.tags = TagMgr.from_string(bmark_tags)
        DBSession.add(bmark)

        test_str = tags[0].name[0:2]
        suggestions = TagMgr.complete(test_str, username=user.username,
                                      requested_by=gen_random_word(10))
        self.assertTrue(
            tags[0] not in suggestions,
            "The sample tag was not found in the completion set")

        # Also check when username is None.
        suggestions = TagMgr.complete(test_str, username=None)
        self.assertTrue(
            tags[0] not in suggestions,
            "The sample tag was not found in the completion set")

    def test_case_insensitive(self):
        """Suggestion does not care about case of the prefix."""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)

        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)
        bmark_tags = u" ".join(tag_names)
        bmark_url = u'http://bmark.us'
        bmark_desc = u'This is a test bookmark'
        bmark_ext = u'Some extended notes'

        # Store the bookmark.
        bmark = make_bookmark(is_private=True)
        bmark.url = bmark_url
        bmark.username = user.username
        bmark.description = bmark_desc
        bmark.extended = bmark_ext
        bmark.tags = TagMgr.from_string(bmark_tags)
        DBSession.add(bmark)

        test_str = tags[0].name[0:4].upper()
        suggestions = TagMgr.complete(test_str, username=user.username,
                                      requested_by=user.username)
        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")
