"""Provide tools for generating objects for testing purposes."""
from random import randint
import random
import string

from bookie.models import Bmark
from bookie.models import Tag


def random_int(max=1000):
    """Generate a random integer value

    :param max: Maximum value to hit.
    """
    return randint(0, max)


def random_string(length=None):
    """Generates a random string from urandom.

    :param length: Specify the number of chars in the generated string.
    """
    chars = string.ascii_uppercase + string.digits
    str_length = length if length is not None else random_int()
    return ''.join(random.choice(chars) for x in range(str_length))


def random_url():
    """Generate a random url that is totally bogus."""
    url = "http://{0}.com".format(random_string)
    return url


def make_tag(name=None):
    if not name:
        name = random_string(255)

    return Tag(name)


def make_bookmark():
    """Generate a fake bookmark for testing use."""
    bmark = Bmark(random_url(),
                  username="admin",
                  desc=random_string(),
                  ext=random_string(),
                  tags=u"bookmarks")
    return bmark
