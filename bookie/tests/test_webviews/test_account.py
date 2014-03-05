"""Tests for the account views"""

import logging
from bookie.tests import TestViewBase
from bookie.tests import gen_random_word

LOG = logging.getLogger(__name__)


class AccountViewsTest(TestViewBase):

    """Test the account web views for a user when deleting all bookmarks"""

    def test_delete_all_bookmarks_with_correct_confirmation(self):
        """Verify the workflow with correct confirmation."""
        self._login_admin()
        res = self.app.post(
            '/admin/account/delete_all_bookmarks',
            params={
                'username': 'admin',
                'delete': 'Delete',
            })

        self.assertEqual(
            res.status,
            "200 OK",
            msg='recent status is 200, ' + res.status)
        self.assertTrue(
            "The delete request has been queued" +
            " and will be acted upon shortly." in res.body,
            msg="Request should contain the appropriate message.")

    def test_delete_all_bookmarks_with_wong_confirmation(self):
        """Verify the workflow with wrong confirmation."""
        self._login_admin()
        res = self.app.post(
            '/admin/account/delete_all_bookmarks',
            params={
                'username': 'admin',
                'delete': gen_random_word(10),
            })

        self.assertEqual(
            res.status,
            "200 OK",
            msg='recent status is 200, ' + res.status)
        self.assertTrue(
            "Delete request not confirmed. Please make sure" +
            " to enter &#39;Delete&#39; to confirm." in res.body,
            msg="Request should contain the appropriate message.")

    def test_delete_all_bookmarks_without_confirmation(self):
        """Verify the workflow without any confirmation."""
        self._login_admin()
        res = self.app.post(
            '/admin/account/delete_all_bookmarks',
            params={
                'username': 'admin',
                'delete': '',
            })

        self.assertEqual(
            res.status,
            "200 OK",
            msg='recent status is 200, ' + res.status)
        self.assertTrue(
            "Delete request not confirmed. Please make sure" +
            " to enter &#39;Delete&#39; to confirm." in res.body,
            msg="Request should contain the appropriate message.")
