About JSON API
==============
For best performance, and so that we can implement an api that meets the
features we hold important we have our own api you can implement. It's JSON
based and will return a standard JSON response for any call

All api calls should be against `https://$yoursite.com/api/v1`.

Remember, the only authentication method is the api key. If your site is not
hosted behind secure http server then it's likely to get stolen. Please think
about this before setting up a server exposed to the internet.

.. toctree::
   :maxdepth: 2

   api/user
   api/account
   api/system
   api/admin
   api/delicious
