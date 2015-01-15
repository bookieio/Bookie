"""Generic and small utilities that are used in Bookie"""
import re
import urllib
from urlparse import (
    urlparse,
    urlsplit,
    urlunsplit)
from textblob import TextBlob


def _generate_nouns_from_url(string):
    res = set()
    if string:
        string = string.replace('_', ' ')
        words = re.findall(r"[\w]+", string)

        clean_path = " ".join(words)
        path_tokens = TextBlob(clean_path)
        title_nouns = path_tokens.noun_phrases
        for result in title_nouns:
            # If result has spaces split it to match our tag system.
            nouns = result.split()
            res.update(nouns)
    return res


def suggest_tags(data):
    """Suggest tags based on the content string `data`"""
    tag_set = set()
    if not data:
        return tag_set

    # The string might be a url that needs some cleanup before we parse for
    # suggestions
    parsed = urlparse(data)

    # Check if title is url. If title is not a string, url, and title will be
    # the same so no need to consider tags from url.
    if parsed.hostname:
        tag_set.update(_generate_nouns_from_url(parsed.path))
    else:
        # If the title is not a url extract nouns from title and the url.
        tag_set.update(_generate_nouns_from_url(data))

    return tag_set


def url_fix(string, charset='UTF-8'):
    """Properly encodes the URL if it contains extended chars."""
    if isinstance(string, unicode):
        string = string.encode(charset)
    scheme, netloc, path, query, fragment = urlsplit(string)
    path = urllib.quote(path, safe='/%+$!*\'(),')
    query = urllib.quote_plus(query, safe=':&%=+$!*\'(),')
    fragment = urllib.quote_plus(fragment, safe=':&%=+$!*\'(),')
    return urlunsplit((scheme, netloc, path, query, fragment))
