----------------------------------
Hosting your Bookie installation
----------------------------------
Right now, we're in full developer mode so hosting is up to you. We help you
get started by running it with the built-in `paste` webserver locally.

However Bookie is a WSGI_ application and can be hosted with web servers such
as Apache_, Nginx_, and Cherokee_. As Bookie matures we'll try to get cookbook
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

    paster serve  --daemon bookie.ini

Then to serve it behind Nginx you need to setup a new virtual host config.

::

    server {
    
        listen   80;
        server_name  bookie;
    
        #set your default location
        location / {
            proxy_pass              http://127.0.0.1:6543/;
            proxy_set_header        Host $host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        X-Forwarded-Proto $scheme;
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

    bookie/bookie/bookie/wsgi.py
    bookie/bookie/bookie/combo.py

With the following:

wsgi.py

::

    #!/usr/bin/python env
    import os
    from os.path import dirname
    
    # Add the virtual Python environment site-packages directory to the path
    import site
    
    ve_dir = dirname(dirname(dirname(dirname(__file__))))
    install_dir = dirname(dirname(__file__))
    
    site.addsitedir(os.path.join(ve_dir, 'lib/python2.6/site-packages'))
    
    # Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
    os.environ['PYTHON_EGG_CACHE'] = os.path.join(install_dir, 'egg-cache')
    
    # Load the application
    from paste.deploy import loadapp
    application = loadapp('config:' + os.path.join(install_dir, 'production.ini'))


combo.py

::

    """WSGI file to serve the combo JS out of convoy"""
    from convoy.combo import combo_app
    JS_FILES = 'bookie/static/js/build'
    application = combo_app(JS_FILES)


uWSGI Config
~~~~~~~~~~~~
Now we need to add the uwsgi daemon settings for this application. We'll create
a file `/etc/init/bookie.conf` that will give us an upstart enabled
service to run the app through.

::

    description "uWSGI Bookie Install"
    start on runlevel [2345]
    stop on runlevel [!2345]
    respawn
    exec /usr/bin/uwsgi26 --socket /tmp/bookie.sock \
    -H /home/$username/bookie/ \
    --chmod-socket --module wsgi \
    --pythonpath /home/$username/bookie/bookie/bookie \
    -p 4

combo loader

::

    description "uWSGI Convoy"
    start on runlevel [2345]
    stop on runlevel [!2345]
    respawn
    exec /usr/bin/uwsgi --socket /tmp/convoy.sock \
    -H /home/$username/bookie \
    --chmod-socket --module combo \
    -p 4 --threads 2


We should not be able to start up the server with uWSGI command there.

::

    sudo /usr/bin/uwsgi26 --socket /tmp/rick.bmark.sock \
    -H /home/$username/bookie/ \
    --chmod-socket --module wsgi \
    --pythonpath /home/$username/bookie/bookie/Bookie/bookie \
    -p 4

This will help bring up any potential errors. If all starts up well you can
launch the daemon with:

::

    $ sudo service bookie start
    $ sudo service combo start

Nginx Config
~~~~~~~~~~~~
Once that's started we just need to tell Nginx where to go access the
application.

::

    server {
      listen 80; 
      server_name bookie;
      charset utf-8;
    
      root /home/$username/bookie/bookie/bookie/static;
      index index.html index.htm;

      # Remove trailing slash by doing a 301 redirect
      rewrite ^/(.*)/$ /$1 permanent;
    
      location ~*/(img|js|iepng|css)/ {
        root /home/$username/bookie/bookie/bookie;
        expires max;
        add_header Cache-Control "public";
        break;
      }
    
      location /combo {
        include     uwsgi_params;
        uwsgi_pass  unix:///tmp/convoy.sock;
        uwsgi_param UWSGI_SCHEME $scheme;
        break;
      }
    
      location / { 
        include     uwsgi_params;
        uwsgi_pass  unix:///tmp/bookie.sock;
        uwsgi_param SCRIPT_NAME /;
        uwsgi_param UWSGI_SCHEME $scheme;
      }

      ## Compression
      # src: http://www.ruby-forum.com/topic/141251
      # src: http://wiki.brightbox.co.uk/docs:nginx
    
      gzip on;
      gzip_http_version 1.0;
      gzip_comp_level 2;
      gzip_proxied any;
      gzip_min_length  1100;
      gzip_buffers 16 8k;
      gzip_types text/plain text/html text/css application/x-javascript application/xml application/xml+rss text/javascript;
    
      # Some version of IE 6 don't handle compression well on some mime-types, so just disable for them
      gzip_disable "MSIE [1-6].(?!.*SV1)";
    
      # Set a vary header so downstream proxies don't send cached gzipped content to IE6
      gzip_vary on;
      ## /Compression
    
    }

From there we just need to check Nginx for any issues and reload it.

::

    sudo nginx -t
    sudo service nginx reload

Hosting with Apache and mod_wsgi
--------------------------------
Apache and the mod_wsgi Apache module is the tried-and-true standard for WSGI serving. It also happens to be really easy to get your Bookie app working with it.

First you need to install Apache and mod_wsgi:

- On a Debian-based Linux (Ubuntu): apt-get install libapache2-mod-wsgi
- On other Linuxes: ?
- On OSX: ?
- On Windows: ?

Then you need to create a pyramid.wsgi file in the root of your Bookie virtualenv. Something like

::

    import os
    os.environ['NLTK_DATA'] = '/home/user/bookie/bookie/download-cache/nltk'
    from pyramid.paster import get_app
    application = get_app('/home/user/bookie/bookie/mybookie.ini', 'bookie')

A couple of things to check:

- The get_app path is correct for your system.
- If you're using SQLite, make sure you use the full path to it in your bookie/bookie/mybookie.ini

Next you need to add a virtualhost to your Apache config. You can either put this right in your httpd.conf or create a virtualhost for it.

::

    WSGIApplicationGroup %{GLOBAL}
    WSGIPassAuthorization On
    WSGIDaemonProcess pyramid user=ben group=ben threads=4 \
        python-path=/home/user/bookie/lib/python2.6/site-packages
    WSGIScriptAlias / /home/user/bookie/pyramid.wsgi

    <Directory /home/user/bookie>
        WSGIProcessGroup pyramid
        Order allow,deny
        Allow from all
    </Directory>

A couple of things you need to check:

- The python-path line matches the path to your virtualenv's site-packages.
- The WSGIScriptAlias in the example serves your Bookie install at the server's root. You can change that if you wish.
- The WSGIScriptAlias path to pyramid.wsgi is correct for your system.
- The Directory path is correct for your system. It should point to your virtualenv's root.

Finally, all you have to do is restart Apache and off you go!

- On a Debian-based Linux (Ubuntu): /etc/init.d/apache2 restart
- On other Linuxes: ?
- On OSX: ?
- On Windows: ?

For more help running Bookie under mod_wsgi on Apache, check out the modwsgi_ Pyramid Docs.

.. _modwsgi: https://docs.pylonsproject.org/projects/pyramid/1.2/tutorials/modwsgi/index.html#modwsgi-tutorial


