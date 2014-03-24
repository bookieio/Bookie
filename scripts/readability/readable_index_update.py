#!/usr/bin/env python

from ConfigParser import ConfigParser
from os import path
from bookie.models import initialize_sql

if __name__ == "__main__":
    ini = ConfigParser()
    ini_path = path.join(
        path.dirname(path.dirname(path.dirname(__file__))),
        'bookie.ini')

    ini.readfp(open(ini_path))
    initialize_sql(dict(ini.items("app:bookie")))

    from bookie.models import Readable
    from bookie.models import Bmark
    from bookie.models.fulltext import get_writer

    writer = get_writer()

    readable_bmarks = Readable.query.all()
    for bmark in readable_bmarks:
        b = Bmark.query.get(bmark.bid)

        if b:
            writer.update_document(
                bid=unicode(b.bid),
                description=b.description if b.description else u"",
                extended=b.extended if b.extended else u"",
                tags=b.tag_str if b.tag_str else u"",
                readable=b.readable.content,
            )
    writer.commit()
