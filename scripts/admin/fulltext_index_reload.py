#!/usr/bin/env python
"""Force the system to refresh the fulltext index.

This is useful because we've had lockup issues with Whoosh and in case we need
to reset, this will force it through celery.

"""
import argparse

from ConfigParser import ConfigParser

# TODO
