#!/usr/bin/env python

"""
Need to install Logbook and inbox to get the smtpsink to work

"""


from inbox import Inbox

PORT = 4467
ADDR = '0.0.0.0'
inbox = Inbox()


@inbox.collate
def handle(*args, **kwargs):
    outfile = open('email_log', 'a')
    for arg in args:
        outfile.write(arg + "\n")

    for key, arg in kwargs.items():
        outfile.write("{0}: {1}".format(key, arg))

    outfile.write('*' * 30)

# Bind directly.
inbox.serve(address=ADDR, port=PORT)
print "serving on {0}:{1}".format(ADDR, PORT)
