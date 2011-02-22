"""Process an html delicious export and import them into bookie"""
import codecs
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from sys import argv
import urllib

DELAPI = 'http://127.0.0.1:6543/delapi/posts/add?'


def process(filename):
    """Given a file, process it"""
    bmark_file = codecs.open( filename, "r", "utf-8" ).read()
    soup = BeautifulSoup(bmark_file)

    for dt in soup.findAll('dt'):
        # if we have a dd as next sibling, get it's content
        if dt.nextSibling and dt.nextSibling.name == 'dd':
            extended = dt.nextSibling.text
        else:
            extended = ""

        link = dt.a

        # now get the link tag
        call_system(link, extended)


def call_system(link_tag, extended):
    """Given a parsed <a> tag, store this"""
    date_fmt = "%Y-%m-%dT%I:%M:%SZ"
    add_date = datetime.fromtimestamp(float(link_tag['add_date']))

    prms = {
            'url': link_tag['href'].encode('utf-8'),
            'description': link_tag.text.encode('utf-8'),
            'extended': extended.encode('utf-8'),
            'tags': " ".join(link_tag['tags'].split(',')).encode('utf-8'),
            'dt': add_date.strftime(date_fmt),
    }



    req_params = urllib.urlencode(prms)

    call = urllib.urlopen(DELAPI + req_params)
    call.close()


if __name__ == "__main__":
    filename = argv[1]
    process(filename)
