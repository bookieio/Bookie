#!/bin/env python

"""Process request times from nginx access lines

The access log has been tweaked to add a request time to the end of the line

This doesn't take into account any network traffic back to the user, so only
server side request time.

We want to grab the top 10 urls and see what's the longest stuff going on

:requires: apachelog but I don't want to make it a full requirement for the
application

"""
import apachelog
import argparse

from collections import defaultdict
from operator import itemgetter

LOG_FMT = """%h %z %z %t \\"%r\\" %>s %b \\"%{Referer}i\\" \\"%{User-Agent}i\\" %x"""


def parse_args():
    """Go through the command line options

    """
    desc = "Check for the longest running requests in bookie"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-l', '--log', dest='log',
                            action='store',
                            default=None,
                            required=True,
                            help="log file we're reading requests from")

    parser.add_argument('-n', '--number', dest='count',
                            action='store',
                            default=10,
                            type=int,
                            required=False,
                            help="how many urls do we wish to see, default 10")


    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    parse = apachelog.parser(LOG_FMT)
    res = []

    with open(args.log) as log:
        for l in log:
            try:
                l = parse.parse(l.strip())
                rtime, url = l['%x'], l['%r']
                res.append((url, rtime))
            except Exception, exc:
                print str(exc)

    for r in sorted(res, key=itemgetter(1), reverse=True)[0:args.count]:
        print "{1} - {0}".format(*r)
