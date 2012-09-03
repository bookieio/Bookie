================
Single user mode
================

If you want manage only one bookmark, your bookmark and disabled signup feature, you
can activate *single user mode* feature.

In your ``.ini`` config file, enable ``single_user_mode`` parameter :

::

    …
    email.host=localhost

    single_user_mode = true

    fulltext.engine=whoosh
    …

The *single user mode* feature :

* hide and disable signup feature
* redirect homepage to all bookmark page
* rename "All" button to "Bookmark"
