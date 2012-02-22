Makefile
===============
Nearly everything about Bookie is managed via the Makefile. If you're not
familiar with Makefiles, it's worth a little time to get your head around.

Common make operations:
------------------------

:make run:
This command will start up the Bookie application along with the combo loader
needed to serve the Javascript for Bookie.

:make stop:
This will kill the running servers started up from the `make run`.

:make js:
This command will check for updated Javascript library files and, if required,
copy changed files to the build directory and minimize them.

:make run_dev:
When doing development you might want some help keeping things "built" while
you work. This command will also start up the sass watch process and a python
script that will auto build changed Javascript files for you.  This is how I
tend to work and debug. For production purposes though, `make run` does
everything you need.

:make stop_dev:
This will kill things started via `make run_dev`.

:make test:
Run the Python tests.

:make jstest:
Open up all of the Javascript tests in the browser, one per tab.

:make db_up:
Run any database migrations.

:make db_new:
Start out a new migration file. Make sure to pass `desc="What is this migration"`.

:make clean:
This will wipe the majority of the built files and resources.  Think of it as
a little bit of a hard reset.

:make all:
Should recover froma a `make clean` and perform steps just as checking all
deps are installed, the database is up to date, and the Javascript and CSS are
up to date.
