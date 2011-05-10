"""Create routes here and gets returned into __init__ main()"""
from pyramid.exceptions import NotFound
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden
from bookie.views.exceptions import resource_not_found
from bookie.views.exceptions import resource_forbidden

import json


class MorJSON:
    def __init__(self, info):
        """ Constructor: info will be an object having the the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary).  """
        pass

    def __call__(self, value, system):
        """ Call a the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """
        request = system.get('request')

        if request is not None:
            request.response_content_type = 'application/json'

        # the dictionary sent back needs to have a success, message, and
        # payload passed in
        if 'success' not in value:
            raise Exception('you must return a success value for a morjson renderer')

        if 'message' not in value:
            raise Exception('you must return a message value for a morjson renderer')

        if 'payload' not in value:
            raise Exception('you must return a payload value for a morjson renderer')

        return self.jsonify(value)

    def jsonify(self, dict_response):
        """Return a json string of the response """
        return json.dumps(dict_response)


def build_routes(config):
    """Add any routes to the config"""

    # add the MorJSON renderer to the list of known ones
    config.add_renderer('morjson', MorJSON)

    config.add_view(resource_not_found,
                    context=NotFound,
                    renderer="exceptions/404.mako")

    config.add_view(resource_not_found,
                    context=HTTPNotFound,
                    renderer="exceptions/404.mako")

    config.add_view(resource_forbidden,
                    context=Forbidden,
                    renderer="exceptions/403.mako")

    config.add_view(resource_forbidden,
                    context=HTTPForbidden,
                    renderer="exceptions/403.mako")

    config.add_route("home", "/")

    # DELAPI Routes
    config.add_route("del_post_add", "/delapi/posts/add")
    config.add_route("del_post_delete", "/delapi/posts/delete")
    config.add_route("del_post_get", "/delapi/posts/get")
    config.add_route("del_tag_complete", "/delapi/tags/complete")

    # bmark routes
    config.add_route("bmark_recent", "/recent")
    config.add_route("bmark_recent_tags", "/recent/*tags")

    config.add_route("bmark_popular", "/popular")
    config.add_route("bmark_popular_tags", "/popular/*tags")

    config.add_route("bmark_delete", "/bmark/delete")
    config.add_route("bmark_confirm_delete", "/bmark/confirm/delete/{bid}")
    config.add_route("bmark_readable", "/bmark/readable/{hash_id}")


    # tag related routes
    # config.add_route("tag_list", "/tags")
    # config.add_route("tag_bmarks_ajax", "/tags/*tags", xhr=True)
    config.add_route("tag_bmarks", "/tags/*tags")

    config.add_route("import", "/import")
    config.add_route("search", "/search")
    config.add_route("search_results", "/results")

    # matches based on the header
    # HTTP_X_REQUESTED_WITH
    config.add_route("search_results_ajax", "/results*terms", xhr=True)
    config.add_route("search_results_rest", "/results*terms")

    config.add_route("export", "/export")
    config.add_route("redirect", "/redirect/{hash_id}")

    return config
