# Makefile to help automate tasks in bookie
WD:=$(shell pwd)
BOOKIE_INI = rick.ini
BOOKIE_JS = bookie/static/js/bookie
BOOKIE_CSS = bookie/static/css
JS_BUILD_PATH = bookie/static/js/build
JS_META_SCRIPT = scripts/js/generate_meta.py
YUIGIT = git://github.com/yui/yui3.git
YUITAG = v3.5.0pr2

EXTENSION = $(WD)/extensions/
CHROME = /usr/bin/google-chrome
CHROME_BUILD = $(EXTENSION)/chrome_ext/lib
CHROME_EXT_PATH = $(EXTENSION)/chrome_ext
CHROME_KEY = /home/rharding/.ssh/chrome_ext.pem
CHROME_FILESERVE = /home/bmark.us/www/bookie_chrome.crx
CHROME_BUILD_FILE = $(EXTENSION)/chrome_ext.crx
CHROME_DEV_FILE = $(EXTENSION)/chrome_ext.zip

CSS = bookie/static/css/bookie.css


S3CP = s3cp.py --bucket files.bmark.us --public

all: js css

js: $(JS_BUILD_PATH)/b/meta.js $(JS_BUILD_PATH)/y
clean_js:
	rm -rf $(JS_BUILD_PATH)/*
	rm -rf /tmp/yui
	rm $(CHROME_BUILD)/y*.js
	rm -rf jsdoc

$(JS_BUILD_PATH)/b/meta.js: $(JS_BUILD_PATH)/b/y*-min.js
	$(JS_META_SCRIPT) -n YUI_MODULES -s $(JS_BUILD_PATH)/b/ \
		-o $(JS_BUILD_PATH)/b/meta.js \
		-x -min.js$
$(JS_BUILD_PATH)/b/y%-min.js: $(JS_BUILD_PATH)/b $(JS_BUILD_PATH)/b/y%.js
	scripts/js/jsmin_all.py $(JS_BUILD_PATH)/b
$(JS_BUILD_PATH)/b/y%.js: $(BOOKIE_JS)/y%.js
	cp $? $(JS_BUILD_PATH)/b/
	cp $? $(CHROME_BUILD)
$(JS_BUILD_PATH)/b:
	mkdir $(JS_BUILD_PATH)/b
$(JS_BUILD_PATH)/y:
	mkdir $(JS_BUILD_PATH)/y
	mkdir /tmp/yui
	git clone --depth 1 $(YUIGIT) /tmp/yui
	cd /tmp/yui && git checkout $(YUITAG)
	cp -r /tmp/yui/build/* $(JS_BUILD_PATH)/y
	rm -rf /tmp/yui

static_upload: js css
	cd $(WD)/$(JS_BUILD_PATH)/b && tar cf $(WD)/bookie_static.tar *.js
	cd $(WD)/$(BOOKIE_CSS) && tar uf $(WD)/bookie_static.tar bookie.css
	cd $(WD)/bookie/static/images && tar uf $(WD)/bookie_static.tar *
	gzip $(WD)/bookie_static.tar
	cd $(WD) && s3cp.py --bucket files.bmark.us --public bookie_static.tar.gz
	rm $(WD)/bookie_static.tar.gz


js_doc: js
	rm $(JS_BUILD_PATH)/b/meta.js $(JS_BUILD_PATH)/b/*-min.js
	yuidoc -o jsdoc $(JS_BUILD_PATH)/b/
js_doc_upload: js_doc
	scp -r jsdoc/* jsdoc jsdoc.bmark.us:/home/bmark.us/jsdocs/

css: chrome_css
chrome_css:
	cp $(CSS) $(CHROME_BUILD)

clean_css:
	rm $(CHROME_BUILD)/*.css


.PHONY: chrome_ext
chrome: clean_chrome
	$(CHROME) --pack-extension=$(CHROME_EXT_PATH) --pack-extension-key=$(CHROME_KEY)

chrome_upload: chrome
	cd $(EXTENSION) && $(S3CP) chrome_ext.crx

.PHONY: clean_chrome
clean_chrome:
	if [ -f $(CHROME_BUILD_FILE)]; then \
		rm $(CHROME_BUILD_FILE); \
	fi

run: run_combo run_css run_app
run_dev: run autojsbuild
run_combo:
	gunicorn -p combo.pid combo:application &
run_css:
	sass --watch bookie/static/css/bookie.scss:bookie/static/css/bookie.css &
run_app:
	paster serve --reload --pid-file=paster.pid $(BOOKIE_INI) &
run_livereload:
	livereload
autojsbuild:
	python scripts/js/autojsbuild.py -w $(BOOKIE_JS) -b $(JS_BUILD_PATH)/b

stop: stop_combo stop_css stop_app
stop_dev: stop
stop_combo:
	kill -9 `cat combo.pid`
	rm combo.pid
stop_css:
	killall -9 sass
stop_app:
	kill -9 `cat paster.pid`
	rm paster.pid
stop_livereload:
	killall livereload

clean: clean_js clean_css

.PHONY: clean clean_js $(JS_BUILD_PATH)/b/meta.js autojsbuild js_doc js_doc_upload\
	run run_dev run_combo run_css run_app run_livereload \
	stop stop_dev stop_app stop_css stop_combo stop_livereload \
	css chrome_css clean_css
