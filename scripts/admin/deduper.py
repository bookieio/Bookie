#!/usr/bin/env python
"""We weren't good and got duplicate bookmarks for users.

This will go through and find bookmarks, per user, with the same hash_id,
combine the tags from one onto the other, and then remove the dupe.

"""
import transaction

from collections import defaultdict
from ConfigParser import ConfigParser
from os import path
from bookie.models import initialize_sql


if __name__ == "__main__":
    ini = ConfigParser()
    ini_path = path.join(path.dirname(path.dirname(path.dirname(__file__))),
        'bookie.ini')

    ini.readfp(open(ini_path))
    initialize_sql(dict(ini.items("app:main")))

    from bookie.models import DBSession
    from bookie.models import Bmark

    bookmarks = Bmark.query.all()
    index = defaultdict(list)
    to_delete = []
    for b in bookmarks:
        key = (b.username, b.hash_id)
        index[key].append(b)

    for k, v in index.iteritems():
        if len(v) > 1:
            first = v[0]
            second = v[1]

            print first.hash_id
            to_delete.append(first)
            for name, tag in first.tags.items():
                if name in second.tags:
                    print "HAS IT"
                else:
                    print "ADDING" + name
                    second.tags[name] = tag

            assert len(first.tags) <= len(second.tags)

    print to_delete
    print len(to_delete)
    for b in to_delete:
        DBSession.delete(b)

    DBSession.flush()
    transaction.commit()
