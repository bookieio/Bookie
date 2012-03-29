"""WSGI file to serve the combo JS out of convoy"""
from convoy.combo import combo_app

JS_FILES = '/home/bmark.us/prod/bookie/bookie/static/js/build'

application = combo_app(JS_FILES)
