#!/usr/bin/env python
from migrate.versioning.shell import main

import bookie
bookie.get_appconfig(with_pylons=True)

main(url=bookie.APP_CONF.get('app:main', 'sqlalchemy.url') ,repository='bookie/migrations')
