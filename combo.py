"""WSGI file to serve the combo JS out of convoy"""
from convoy.combo import combo_app

JS_FILES = 'bookie/static/js/build'

application = combo_app(JS_FILES)
