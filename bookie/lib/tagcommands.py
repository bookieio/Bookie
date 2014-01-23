"""Allow for tag based commands to act upon the bookmarks in the system

"""
import logging
from bookie.models import TagMgr

LOG = logging.getLogger(__name__)
COMMANDLIST = {}


class Commander(object):

    def __init__(self, bmark):
        self.commands = []
        self.bmark = bmark

    @staticmethod
    def check_commands(tags):
        """Pretend to build up a list of commands based on the tags passed"""
        return [tag for tag in tags.keys() if tag in COMMANDLIST]

    def build_commands(self):
        """See if we ehave any commands to apply to this bookmark"""
        for tag in self.bmark.tags.keys():
            # if this tag is a command then return true
            if tag in COMMANDLIST:
                self.commands.append(tag)

    def process(self):
        """see if there are any known commands and process them"""
        self.build_commands()

        for cmd in self.commands:
            # remove the tag from the bookmark
            del(self.bmark.tags[cmd])

            # run the command given the current state of the bookmark
            self.bmark = COMMANDLIST[cmd].run(self.bmark)

        return self.bmark


class Command(object):
    """Base of a command

    api is basically a run() method that accepts the bookmark in question

    """

    def run(bmark):
        """Run the command with the given Bmark object"""
        raise Exception("Not implemented")


class ToRead(Command):
    """Command to mark a bookmark as toread"""
    command_tag = u"!toread"
    read_tag = u"toread"

    @staticmethod
    def run(bmark):
        """Update this bookmark to toread status"""
        if ToRead.read_tag not in bmark.tags:
            res = TagMgr.find(tags=[ToRead.read_tag])
            if res:
                bmark.tags[ToRead.read_tag] = res[0]

        return bmark

# add our command to the list of those available
COMMANDLIST[ToRead.command_tag] = ToRead


class IsRead(Command):
    """Command to mark a bookmark as read

    This is basically just removing to toread tag from the bookmark
    It's just doing it as a command vs a manual edit to the tags

    """
    command_tag = "!read"
    read_tag = "toread"

    @staticmethod
    def run(bmark):
        """Make sure we remove the toread tag"""
        if IsRead.read_tag in bmark.tags:
            del(bmark.tags[IsRead.read_tag])

        return bmark

# add our command to the list of those available
COMMANDLIST[IsRead.command_tag] = IsRead
