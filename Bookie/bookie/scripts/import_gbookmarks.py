"""Process an html google bookmarks export and import them into bookie"""
import codecs
import time
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from collections import defaultdict
from sys import argv
import urllib

DELAPI = 'http://127.0.0.1:6543/delapi/posts/add?'


def process(fname):
    """Given a filename in google bookmark's export format, import it 

    The export format is a tag as a heading, with urls that have that tag
    under that heading. If a url has N tags, it will appear N times, once
    under each heading.
    """
    bmark_file = codecs.open(fname, "r", "utf-8").read()
    soup = BeautifulSoup(bmark_file)
    if not soup.contents[0] == "DOCTYPE NETSCAPE-Bookmark-file-1":
        raise Exception("File does not appear to be a google bookmarks export")

    urls = dict() # url:url_metadata

    # we don't want to just import all the available urls, since each url 
    # occurs once per tag. loop through and aggregate the tags for each url
    for tag in soup.findAll('h3'): 
        links = tag.findNextSibling('dl').findAll("a")
        for l in links:
            url = l["href"]
            if url in urls:
                urls[url]['tags'].append(tag.text) 
            else:
                urls[url] = {
                    'description': l.text,
                    'tags': [tag.text] if tag.text != 'Unlabeled' else [],
                    'date_added': datetime.fromtimestamp(float(l['add_date'])/1e6),
                }

    call_system(urls)

def call_system(urls):
    """Given a dictionary of url data, store it"""
    date_fmt = "%Y-%m-%dT%H:%M:%SZ"
    for url,metadata in urls.items():
        prms = {
                'url': url.encode('utf-8'),
                'description': metadata['description'].encode('utf-8'),
                'tags': " ".join(metadata['tags']).encode('utf-8'),
                'dt': metadata['date_added'].strftime(date_fmt),
        }
        req_params = urllib.urlencode(prms)
        call = urllib.urlopen(DELAPI + req_params)
        call.close()

if __name__ == "__main__":
    filename = argv[1]
    process(filename)
