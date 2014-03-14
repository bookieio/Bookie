# Makefile to help automate tasks in bookie
WD := $(shell pwd)
PY := bin/python
ALEMBIC := $(PY) bin/alembic
CELERY := $(PY) bin/celery worker --app=bookie.bcelery -B -l debug
PEP8 := $(PY) bin/pep8
PIP := $(PY) bin/pip
PIP_MIR = PIP_FIND_LINKS='http://mypi http://simple.crate.io/'
NOSE := $(PY) bin/nose2
PYTEST := $(PY) bin/py.test
PASTER := $(PY) bin/pserve
PYSCSS := $(PY) bin/pyscss
GUNICORN := $(PY) bin/gunicorn
S3 := s3cp.py --bucket files.bmark.us --public

BOOKIE_INI = bookie.ini
SAURL = $(shell grep sqlalchemy.url $(BOOKIE_INI) | cut -d "=" -f 2 | tr -d " ")

CACHE := "$(WD)/download-cache"
BOOKIE_JS = bookie/static/js/bookie
JS_BUILD_PATH = bookie/static/js/build
JS_META_SCRIPT = $(PY) scripts/js/generate_meta.py
DEV_JS_FILES := $(wildcard $(BOOKIE_JS)/*.js)
BUILD_JS_FILES := $(patsubst $(BOOKIE_JS)/%.js,$(JS_BUILD_PATH)/b/%.js,$(DEV_JS_FILES))
BUILD_JSMIN_FILES := $(patsubst $(JS_BUILD_PATH)/b/%.js,,$(JS_BUILD_PATH)/b/%-min.js,$(BUILD_JS_FILES))
YUI := yui_3.11.0.zip
JSTESTURL = http://127.0.0.1:9000/tests

EXTENSION = "$(WD)/extensions"
CHROME = /usr/bin/google-chrome
CHROME_BUILD = $(EXTENSION)/chrome_ext/lib
CHROME_EXT_PATH = $(EXTENSION)/chrome_ext
CHROME_KEY = /home/rharding/.ssh/chrome_ext.pem
CHROME_FILESERVE = /home/bmark.us/www/bookie_chrome.crx
CHROME_BUILD_FILE = $(EXTENSION)/chrome_ext.crx
CHROME_DEV_FILE = $(EXTENSION)/chrome_ext.zip

BOOKIE_CSS = bookie/static/css
RESCSS = bookie/static/css/responsive.css
BASECSS = bookie/static/css/base.css

SYSDEPS_UBUNTU = build-essential libxslt1-dev libxml2-dev python-dev libpq-dev git\
	       python-virtualenv redis-server unzip
SYSDEPS_ARCH =  base-devel libxslt libxml2 python postgresql-libs git\
				 python-virtualenv redis unzip
SYSDEPS_FEDORA = automake gcc gcc-c++ libxslt-devel libxml2-devel python-devel\
				 libpqxx-devel git python-virtualenv redis unzip

.PHONY: all
all: deps develop bookie.db db_up js

.PHONY: clean
clean: clean_js clean_css

.PHONY: clean_all
clean_all: clean_venv clean_js clean_css clean_chrome clean_downloadcache

.PHONY: sysdeps
sysdeps:
	if which apt-get &> /dev/null; then \
		if [ $(NONINTERACTIVE) ]; then \
			sudo apt-get install -y $(SYSDEPS_UBUNTU); \
		else \
			sudo apt-get install $(SYSDEPS_UBUNTU); \
		fi \
	elif which pacman &> /dev/null; then \
		if [ $(NONINTERACTIVE) ]; then \
			sudo pacman -S --noconfirm $(SYSDEPS_ARCH); \
		else \
			sudo pacman -S $(SYSDEPS_ARCH); \
		fi; \
		sudo systemctl start redis; \
	elif which yum &> /dev/null; then \
		if [ $(NONINTERACTIVE) ]; then \
			sudo yum install -y $(SYSDEPS_FEDORA); \
		else \
			sudo yum install $(SYSDEPS_FEDORA); \
		fi; \
		sudo service redis start; \
	fi

.PHONY: install
install: $(BOOKIE_INI) all first_bookmark css

.PHONY: develop
develop: lib/python*/site-packages/bookie.egg-link
lib/python*/site-packages/bookie.egg-link:
	$(PY) setup.py develop

$(BOOKIE_INI):
	cp sample.ini $(BOOKIE_INI)

# DATABASE
#
# Need a series of commands to handle migrations
bookie.db: develop
	$(ALEMBIC) upgrade head

test_bookie.db: develop
	$(ALEMBIC) -c test_alembic.ini upgrade head

# The upgade/etc commands are only for the live db. Test databases are
# expected to be torn down and resetup each time.
.PHONY: db_up
db_up: bookie.db
	$(ALEMBIC) upgrade head

.PHONY: db_down
db_down: bookie.db
	$(ALEMBIC) downgrade

# make db_new desc="This is a new migration"
.PHONY: db_new
db_new: bookie.db
	$(ALEMBIC) revision -m "$(desc)"

.PHONY: db_version
db_version: bookie.db
	$(ALEMBIC) current

.PHONY: first_bookmark
first_bookmark: develop
	$(PY) scripts/admin/first_bookmark.py

# DOCS
#
# docs are built from sphinx locally. They're hosted remotely using
# readthedocs.org though, so we don't need anything to upload/push them.

.PHONY: docs
docs:
	cd docs && make html

.PHONY: docs_upload
docs_open: docs
	xdg-open docs/_build/html/index.html

# Generate ctags for the code in the project
.PHONY: tags
tags:
	ctags --tag-relative --python-kinds=-iv -Rf tags-py --sort=yes --exclude=.git --languages=python

.PHONY: lint
lint:
	flake8 bookie/

# DEPS
#
# Install the packages we need.

.PHONY: deps
deps: venv
	@echo "\n\nSilently installing packages (this will take a while)..."
	if test -d download-cache; \
		then cd download-cache && git pull origin master || true; \
		else git clone --depth=1 "http://github.com/mitechie/bookie-download-cache.git" download-cache; \
	fi
	@echo "Making sure the latest version of pip is available"
	# $(PIP) install -U pip
	$(PIP) install --no-index --no-dependencies --find-links file:///$(CACHE)/python -r requirements.txt

# TESTS
#
# Tools for running python and javascript tests

.PHONY: smtp
smtp:
	$(PY) scripts/misc/smtpsink.py

.PHONY: test
test:
	INI="test.ini" $(PYTEST) -s bookie/tests

.PHONY: testcoverage
testcoverage:
	$(NOSE) --with-coverage --cover-html --cover-package=bookie bookie/tests

.PHONY: clean_testdb
clean_testdb:
	- rm test_bookie.db

.PHONY: builder_test
builder_test: clean_testdb test_bookie.db
	# $(NOSE) -vx --with-id 61 bookie/tests
	$(NOSE) -v --with-coverage --with-id --cover-package=bookie --cover-erase --with-xunit bookie/tests

.PHONY: mysql_test
mysql_test:
	$(PIP_MIR) $(PIP) install PyMySQL
	mysql -u jenkins_bookie --password=bookie -e "DROP DATABASE jenkins_bookie;"
	mysql -u jenkins_bookie --password=bookie -e "CREATE DATABASE jenkins_bookie;"
	bin/alembic -c test_alembic_mysql.ini upgrade head
	BOOKIE_TEST_INI=test_mysql.ini $(NOSE) -xv --with-coverage --cover-package=bookie --cover-erase --with-xunit bookie/tests

.PHONY: pgsql_test
pgsql_test:
	#$(PIP_MIR) $(PIP) install PyMySQL
	#mysql -u jenkins_bookie --password=bookie -e "DROP DATABASE jenkins_bookie;"
	#mysql -u jenkins_bookie --password=bookie -e "CREATE DATABASE jenkins_bookie;"
	bin/alembic -c test_alembic_pgsql.ini upgrade head
	BOOKIE_TEST_INI=test_pgsql.ini $(NOSE) -xv --with-coverage --cover-package=bookie --cover-erase --with-xunit bookie/tests



.PHONY: jstestserver
jstestserver:
	cd bookie/static/js && "$(WD)/$(PY)" -m SimpleHTTPServer 9000
.PHONY: jstest
jstest: test_api test_history test_model test_rsswatch test_view test_indicator test_tagcontrol
.PHONY: jstest_index
jstest_index:
	xdg-open http://127.0.0.1:6543/tests/index
.PHONY: test_api
test_api:
	xdg-open $(JSTESTURL)/test_api.html
.PHONY: test_history
test_history:
	xdg-open $(JSTESTURL)/test_history.html
.PHONY: test_indicator
test_indicator:
	xdg-open $(JSTESTURL)/test_indicator.html
.PHONY: test_model
test_model:
	xdg-open $(JSTESTURL)/test_model.html
.PHONY: test_readable
test_readable:
	xdg-open $(JSTESTURL)/test_readable.html
.PHONY: test_rsswatch
test_rsswatch:
	xdg-open $(JSTESTURL)/test_rsswatch.html
.PHONY: test_tagcontrol
test_tagcontrol:
	xdg-open $(JSTESTURL)/test_tagcontrol.html
.PHONY: test_userstats
test_userstats:
	xdg-open $(JSTESTURL)/test_user_stats.html
.PHONY: test_view
test_view:
	xdg-open $(JSTESTURL)/test_view.html

.PHONY: pep8
pep8:
	$(PEP8) bookie/ > pep8.out

# JAVASCRIPT
#
# Javascript tools for building out combo loader build directory, out meta.js,
# and syncing things over to the chrome extension directory.

.PHONY: js
js: js_dirs jsmin bookie/static/js/tests/jstpl.html $(JS_BUILD_PATH)/b/meta.js

.PHONY: js_dirs
js_dirs: $(JS_BUILD_PATH)/b $(JS_BUILD_PATH)/y $(CHROME_BUILD)

$(CHROME_BUILD):
	mkdir -p $(CHROME_BUILD)

$(JS_BUILD_PATH)/b:
	mkdir -p $(JS_BUILD_PATH)/b

$(JS_BUILD_PATH)/y: download-cache/yui
	mkdir -p $(JS_BUILD_PATH)/y
	cp -r download-cache/yui/build/* $(JS_BUILD_PATH)/y

bookie/static/js/tests/jstpl.html: bookie/templates/jstpl.mako
	cp bookie/templates/jstpl.mako bookie/static/js/tests/jstpl.html

download-cache/yui:
	mkdir -p download-cache/yui
	unzip download-cache/js/$(YUI) -d download-cache

.PHONY: jsmin
jsmin: $(BUILD_JS_FILES)
	rm $(JS_BUILD_PATH)/b/meta.js || true
	chmod +x scripts/js/jsmin_all.py
	scripts/js/jsmin_all.py $(JS_BUILD_PATH)/b

$(JS_BUILD_PATH)/b/meta.js: $(BUILD_JS_FILES)
	$(JS_META_SCRIPT) -n YUI_MODULES -s $(JS_BUILD_PATH)/b/ \
		-o $(JS_BUILD_PATH)/b/meta.js \
		-x -min.js$

$(BUILD_JSMIN_FILES): $(BUILD_JS_FILES)
	rm $(JS_BUILD_PATH)/b/meta.js || true
	scripts/js/jsmin_all.py $@

$(BUILD_JS_FILES): $(DEV_JS_FILES)
	cp $(BOOKIE_JS)/$(@F) $@
	cp $(BOOKIE_JS)/$(@F) $(CHROME_BUILD)/$(@F)

.PHONY: clean_js
clean_js:
	rm -rf $(JS_BUILD_PATH)/* || true
	rm $(CHROME_BUILD)/*.js || true
	rm -rf jsdoc || true

.PHONY: clean_downloadcache
clean_downloadcache:
	rm -rf download-cache || true

static_upload: js css
	cd "$(WD)/$(JS_BUILD_PATH)/b" && tar cf "$(WD)/bookie_static.tar" *.js
	cd "$(WD)/$(BOOKIE_CSS)" && tar uf "$(WD)/bookie_static.tar" base.css
	cd "$(WD)/bookie/static/images" && tar uf "$(WD)/bookie_static.tar" *
	gzip "$(WD)/bookie_static.tar"
	cd "$(WD) && $(S3) bookie_static.tar.gz"
	rm "$(WD)/bookie_static.tar.gz"

js_doc: js
	rm $(JS_BUILD_PATH)/b/meta.js $(JS_BUILD_PATH)/b/*-min.js
	yuidoc -T simple -o jsdoc $(JS_BUILD_PATH)/b/
	sed -i 's/&#x2F;/\//g' jsdoc/**/*.html
	sed -i 's/&amp;#x2F;/\//g' jsdoc/**/*.html
js_doc_upload: js_doc
	scp -r jsdoc/* jsdoc jsdoc.bmark.us:/home/bmark.us/jsdocs/

css:
	$(PYSCSS) -I bookie/static/css/ -o bookie/static/css/base.css bookie/static/css/base.scss
	$(PYSCSS) -I bookie/static/css/ -o bookie/static/css/responsive.css bookie/static/css/responsive.scss
chrome_css:  $(CHROME_BUILD) css
	cp $(BASECSS) $(CHROME_BUILD)/
	wget "https://bmark.us/combo?y/cssreset/reset-min.css&y/cssfonts/cssfonts-min.css&y/cssgrids/cssgrids-min.css&y/cssbase/cssbase-min.css&y/widget-base/assets/skins/sam/widget-base.css&y/autocomplete-list/assets/skins/sam/autocomplete-list.css" -O $(CHROME_BUILD)/combo.css
clean_css:
	rm $(BOOKIE_CSS)/*.css || true
	rm $(CHROME_BUILD)/*.css || true

# CHROME
#
# Helpers for dealing with the Chrome extension such as building the
# extension, copying it up to files.bmark.us, and such.

.PHONY: chrome_ext
chrome: clean_chrome chrome_css chrome_combo
	$(CHROME) --pack-extension=$(CHROME_EXT_PATH) --pack-extension-key=$(CHROME_KEY)
	cd $(CHROME_EXT_PATH) && zip -r $(CHROME_DEV_FILE) .

chrome_combo:
	wget "https://bmark.us/4006/combo?y/yui/yui-min.js&y/loader/loader-min.js&y/substitute/substitute-min.js&b/meta.js&y/attribute-core/attribute-core-min.js&y/base-core/base-core-min.js&y/oop/oop-min.js&y/event-custom-base/event-custom-base-min.js&y/event-custom-complex/event-custom-complex-min.js&y/attribute-events/attribute-events-min.js&y/attribute-extras/attribute-extras-min.js&y/attribute-base/attribute-base-min.js&y/attribute-complex/attribute-complex-min.js&y/base-base/base-base-min.js&y/pluginhost-base/pluginhost-base-min.js&y/pluginhost-config/pluginhost-config-min.js&y/base-pluginhost/base-pluginhost-min.js&y/base-build/base-build-min.js&y/querystring-stringify-simple/querystring-stringify-simple-min.js&y/io-base/io-base-min.js&y/datatype-xml-parse/datatype-xml-parse-min.js&y/io-xdr/io-xdr-min.js&y/dom-core/dom-core-min.js&y/dom-base/dom-base-min.js&y/selector-native/selector-native-min.js&y/selector/selector-min.js&y/node-core/node-core-min.js&y/node-base/node-base-min.js&y/event-base/event-base-min.js&y/io-form/io-form-min.js&y/io-upload-iframe/io-upload-iframe-min.js&y/queue-promote/queue-promote-min.js&y/io-queue/io-queue-min.js&y/json-parse/json-parse-min.js&y/json-stringify/json-stringify-min.js&y/history-base/history-base-min.js&y/event-synthetic/event-synthetic-min.js&y/history-html5/history-html5-min.js&y/history-hash/history-hash-min.js&y/history-hash-ie/history-hash-ie-min.js&y/array-extras/array-extras-min.js&y/querystring-parse/querystring-parse-min.js&y/querystring-stringify/querystring-stringify-min.js" -O $(CHROME_BUILD)/combo1.js
	wget "https://bmark.us/4006/combo?y/handlebars-compiler/handlebars-compiler-min.js&y/transition/transition-min.js&y/escape/escape-min.js&y/model/model-min.js&y/array-invoke/array-invoke-min.js&y/arraylist/arraylist-min.js&y/model-list/model-list-min.js&y/intl/intl-min.js&y/event-focus/event-focus-min.js&y/event-valuechange/event-valuechange-min.js&y/autocomplete-base/autocomplete-base-min.js&y/autocomplete-sources/autocomplete-sources-min.js&y/autocomplete-list/lang/autocomplete-list_en.js&y/event-resize/event-resize-min.js&y/dom-style/dom-style-min.js&y/dom-screen/dom-screen-min.js&y/node-screen/node-screen-min.js&y/selector-css2/selector-css2-min.js&y/selector-css3/selector-css3-min.js&y/node-style/node-style-min.js&y/node-pluginhost/node-pluginhost-min.js&y/shim-plugin/shim-plugin-min.js&y/classnamemanager/classnamemanager-min.js&y/widget-base/widget-base-min.js&y/widget-htmlparser/widget-htmlparser-min.js&y/event-delegate/event-delegate-min.js&y/node-event-delegate/node-event-delegate-min.js&y/widget-uievents/widget-uievents-min.js&y/widget-skin/widget-skin-min.js&y/widget-position/widget-position-min.js&y/widget-position-align/widget-position-align-min.js&y/autocomplete-list/autocomplete-list-min.js&y/autocomplete-list-keys/autocomplete-list-keys-min.js&y/autocomplete-plugin/autocomplete-plugin-min.js&y/text-data-wordbreak/text-data-wordbreak-min.js&y/text-wordbreak/text-wordbreak-min.js&y/highlight-base/highlight-base-min.js&y/autocomplete-highlighters/autocomplete-highlighters-min.js&y/handlebars-base/handlebars-base-min.js&y/view/view-min.js" -O $(CHROME_BUILD)/combo2.js

chrome_upload: chrome
	cd $(EXTENSION) && $(S3) chrome_ext.crx

.PHONY: clean_chrome
clean_chrome:
	if [ -f $(CHROME_BUILD_FILE) ]; then \
		rm $(CHROME_BUILD_FILE); \
	fi
	if [ -f $(CHROME_DEV_FILE) ]; then \
		rm $(CHROME_DEV_FILE); \
	fi


.PHONY: run
run: run_celery run_app
.PHONY: run_dev
run_dev: run run_css autojsbuild
.PHONY: run_celery
run_celery:
	BOOKIE_INI=$(BOOKIE_INI) $(CELERY) --pidfile celeryd.pid &
.PHONY: run_css
run_css:
	$(PYSCSS) --watch bookie/static/css &
.PHONY: run_prod
run_prod:
	$(PASTER) --pid-file=app.pid $(BOOKIE_INI) &
.PHONY: run_app
run_app:
	$(PASTER) --reload $(BOOKIE_INI)
.PHONY: run_livereload
run_livereload:
	livereload
.PHONY: autojsbuild
autojsbuild:
	$(PY) scripts/js/autojsbuild.py -w $(BOOKIE_JS) -b $(JS_BUILD_PATH)/b

.PHONY: stop
stop: stop_app stop_celery
.PHONY: stop_dev
stop_dev: stop stop_css
.PHONY: stop_celery
stop_celery:
	kill -9 `cat celeryd.pid` || true
	rm celeryd.pid || true
.PHONY: stop_css
stop_css:
	killall -9 scss
.PHONY: stop_app
stop_app:
	kill -9 `cat app.pid` || true
	rm app.pid || true
.PHONY: stop_livereload
stop_livereload:
	killall livereload || true


# INSTALL
#
# Crap to help us install and setup Bookie
# We need a virtualenv
.PHONY: venv
venv: bin/python
bin/python:
	virtualenv -p python2 .

.PHONY: clean_venv
clean_venv:
	rm -rf lib include local bin
