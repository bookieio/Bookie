"""Test the tag commands system"""
from nose.tools import ok_
from unittest import TestCase
from bookie.lib.tagcommands import COMMANDLIST
from bookie.lib.tagcommands import Commander
from bookie.lib.tagcommands import ToRead


# tags act as a dict on the Bmark object, so we're just mocking things
# out a bit simpler using that metaphor.
class BmarkMock(object):

    def __init__(self):
        self.tags = {}

class CommandMock(object):

    @staticmethod
    def run(bmark):
        return bmark


class TestTagCommander(TestCase):
    """Commander system"""

    def setUp(self):
        """Store off the commands so we can return them"""
        self.saved_commandlist = COMMANDLIST
        for key in COMMANDLIST.keys():
            del(COMMANDLIST[key])

    def tearDown(self):
        """Make sure we clear the commands we put in there"""
        for key in self.saved_commandlist:
            COMMANDLIST[key] = self.saved_commandlist[key]

    def test_command_finds_commands(self):
        """Verify we find commands that we know about"""
        COMMANDLIST['!toread'] = lambda bmark: bmark

        bm = BmarkMock()
        bm.tags['!toread'] = True
        commander = Commander(bm)
        commander.build_commands()

        ok_('!toread' in commander.commands,
                "Our commander should find !toread command to run")

    def test_command_tags_removed(self):
        """Test that the command tags are not left over in bmark object"""

        COMMANDLIST['!toread'] = CommandMock


        bm = BmarkMock()
        bm.tags['!toread'] = True
        commander = Commander(bm)
        updated = commander.process()

        ok_('!toread' not in updated.tags,
                "Our commander should find !toread command to run")


class TestToRead(TestCase):
    """Test the ToRead Command"""

    def setUp(self):
        """Store off the commands so we can return them"""
        self.saved_commandlist = COMMANDLIST
        for key in COMMANDLIST.keys():
            del(COMMANDLIST[key])

    def tearDown(self):
        """Make sure we clear the commands we put in there"""
        for key in self.saved_commandlist:
            COMMANDLIST[key] = self.saved_commandlist[key]

    def test_toread_command(self):
        """If marked toread, then should end up with tag 'toread' on it"""
        bm = BmarkMock()
        updated = ToRead.run(bm)
        ok_('toread' in updated.tags,
                "Updated bmark should have 'toread' tag set")

    def test_toread_in_commandset(self):
        """Make sure we can process this command through the commander"""
        COMMANDLIST['!toread'] = ToRead

        bm = BmarkMock()
        bm.tags['!toread'] = True
        commander = Commander(bm)
        updated = commander.process()

        ok_('toread' in updated.tags,
                "Should have the toread tag in the updated bookmark")
        ok_('!toread' not in updated.tags,
                "Should not have the !toread tag in the updated bookmark")

