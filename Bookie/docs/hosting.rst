----------------------------------
Hosting your Bookie installation
----------------------------------
Right now, we're in full developer mode so hosting is up to you. We help you
get started by running it with the built-in `paste` webserver locally.

However Bookie is a WSGI_ application and can be hosted with web servers such
as Apache, Nginx, and Cherokee. As Bookie matures we'll try to get cookbook
docs for using each. For now, it's up to you to figure out, but feel free to
drop by the *#bookie#* irc channel on Freenode for assistance..


.. _WSGI: http://wsgi.org/wsgi/
.. _Apache: http://code.google.com/p/modwsgi/
.. _Nginx: http://wiki.nginx.org/HttpUwsgiModule
.. _Cherokee: http://www.cherokee-project.com/doc/cookbook_uwsgi.html

Nginx proxy to Paster
-----------------------
To start out, the easiest thing to do is to put a web server in front the
paster development server. So you run the web server with the command:

::

    paster serve  --daemon $my.ini

Then to serve it behind Nginx you need to setup a new virtual host config.

::

    server {
    
        listen   80;
        server_name  bookie;
    
        #set your default location
        location / {
         proxy_pass         http://127.0.0.1:6543/;
        }
    }

Now you can create an alias in your */etc/hosts*

::

    127.0.0.1 bookie

now *http://bookie* should be served through Nginx to your bookie instance.


Hosting with Nginx + uWSGI
---------------------------
uWSGI is a great way to run WSGI apps. Nginx is then setup to be the front end
and communicate with the uWSGI processes running.

Warning, this isn't the easiest way to set things up, but it's pretty fast and
decent to run.

wsgi.py
~~~~~~~
First, you need a *wsgi.py* file that tells uWSGI where your environemnt and
application are to run.

Please this file into your application's bookie app directory. If you've used
the normal bootstrap process it should be in:

::

    bookie/bookie/Bookie/bookie/wsgi.py

With the following:

::

    #!/usr/bin/python env
    
    # Add the virtual Python environment site-packages directory to the path
    import site

    # this is the path to the virtualenv you're running bookie from
    site.addsitedir('/home/$username/bookie/lib/python2.6/site-packages')

    # Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
    import os
    os.environ['PYTHON_EGG_CACHE'] = '/home/$username/bookie/bookie/Bookie/egg-cache'

    # Load the application
    from paste.deploy import loadapp
    application = loadapp('config:/home/$username/bookie/bookie/Bookie/$myinstall.ini')

uWSGI Config
~~~~~~~~~~~~
Now we need to add the uwsgi daemon settings for this application. We'll create
a file `/etc/init/rick.bookie.conf` that will give us an upstart enabled
service to run the app through.

::

    description "uWSGI Bookie Install"
    start on runlevel [2345]
    stop on runlevel [!2345]
    respawn
    exec /usr/bin/uwsgi26 --socket /tmp/rick.bookie.sock \
    -H /home/$username/bookie/ \
    --chmod-socket --module wsgi \
    --pythonpath /home/$username/bookie/bookie/Bookie/bookie \
    -p 4

We should not be able to start up the server with uWSGI command there.

::

    sudo /usr/bin/uwsgi26 --socket /tmp/rick.bmark.sock \
    -H /home/$username/bookie/ \
    --chmod-socket --module wsgi \
    --pythonpath /home/$username/bookie/bookie/Bookie/Bookie/bookie \
    -p 4

This will help bring up any potential errors. If all starts up well you can
launch the daemon with:

::

    $ sudo service rick.bmark start

Nginx Config
~~~~~~~~~~~~
Once that's started we just need to tell Nginx where to go access the
application.

::

    server {
      listen 80; 
      server_name bookie;
      charset utf-8;
    
      root /home/$username/bookie/bookie/Bookie/bookie/static;
      index index.html index.htm;
    
      location ~*/(img|js|iepng|css)/ {
        root /home/$username/bookie/bookie/Bookie/bookie;
        expires max;
        add_header Cache-Control "public";
        break;
      }
    
      location / { 
        include     uwsgi_params;
        uwsgi_pass  unix:///tmp/rick.bmark.sock;
        uwsgi_param SCRIPT_NAME /;
      }
    
    }

From there we just need to check Nginx for any issues and reload it.

::

    sudo nginx -t
    sudo service nginx reload


