#!/usr/bin/env python
"""Celery config for Bookie Instance"""
from bookie.bcelery import load_config
print 'loading tasks'

ini = load_config()

print 'finished loading config'

import bookie.bcelery.tasks
bookie.bcelery.tasks.ini_items = ini
