#!/usr/bin/env python
from datetime import date
import gzip
import logging
import os
import urllib

EXPORT_URL = "http://rick.bmark.us/export"
BACKUP_DIR = '/home/rharding/bookie'

LOG = logging.getLogger(__name__)
BACKUP_FILE = "bookie_export_{0}".format(date.today().strftime('%Y_%m_%d'))

if __name__ == "__main__":
    export = urllib.urlopen(EXPORT_URL)
    backup = gzip.open(os.path.join(BACKUP_DIR, BACKUP_FILE + '.gz'), 'w')
    backup.write(export.read())
    export.close()
    backup.close()
