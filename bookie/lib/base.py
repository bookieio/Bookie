"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from pylons import request, tmpl_context as tpl

from bookie.model.meta import Session
from bookie.model.auth import  User
from morpylons.lib import auth


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        # make available any detailed login information we want on all requests
        # if there's no user set, just setup a blank instance
        tpl.current_user = auth.get_user(User()) 

        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            # auto commit at the end of a request
            Session.commit()
            Session.remove()
