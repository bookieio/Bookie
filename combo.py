"""WSGI file to serve the combo JS out of convoy"""
import os
from convoy.combo import combo_app

root_dir = os.path.dirname(__file__)
JS_FILES = root_dir + '/bookie/static/js/build'
application = combo_app(JS_FILES)
