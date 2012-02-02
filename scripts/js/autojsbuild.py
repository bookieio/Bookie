#!/usr/bin/env python
import argparse
import os
import pyinotify
import re
import subprocess

BUILDDIR = '/tmp'
REJS = re.compile('\.js$')
TEST_INDICATOR = 'test'


def parse_args():
    """Go through the command line options

    """
    desc = "Run a file watcher to auto build JS files as they're changed"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-w', '--watch-dir', dest='watch_dir',
                            action='store',
                            default=os.getcwd(),
                            help="What directory are we watching for changes, defaults to cwd")

    parser.add_argument('-b', '--build-dir', dest='build_dir',
                            action='store',
                            required=True,
                            help="Where are we building files to?")

    args = parser.parse_args()
    return args


class event_handler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        dispatch(event.pathname)

    def process_IN_MODIFY(self, event):
        dispatch(event.pathname)


def dispatch(fname):
    """Based on the file that's fired, process its build step

    """
    if is_js_file(fname) and BUILDDIR not in fname:
        process_js_file(fname)


def is_js_file(fname):
    """Check if this file is a .js file that needs to be built"""
    return REJS.search(fname) and \
        TEST_INDICATOR not in fname


def process_js_file(fname):
    """Build a JS file

        - should we keep the path/home with it
        - copy the file to the right place in the build dir
        - create a .min version of the file in that same place
    """
    subprocess.call('make js', shell=True)


def main(watch_dir, build_dir):
    # watch manager
    wm = pyinotify.WatchManager()
    wm.add_watch(watch_dir, pyinotify.ALL_EVENTS, rec=True)

    # event handler
    eh = event_handler()

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()

if __name__ == '__main__':
    args = parse_args()

    if os.path.isdir(args.build_dir):
        BUILD_DIR = args.build_dir
    else:
        raise Exception("Cannot find dir: " + args.build_dir)


    # check the dir exists
    if os.path.isdir(args.watch_dir):
        main(args.watch_dir, args.build_dir)
    else:
        raise Exception("Cannot find dir: " + args.watch_dir)
