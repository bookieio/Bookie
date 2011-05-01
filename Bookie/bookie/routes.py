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

    config.add_route("home", "", view="bookie.views.my_view",
                     view_renderer="/testmako.mako")

    # DELAPI Routes
    config.add_route("del_post_add", "/delapi/posts/add",
                     view="bookie.views.delapi.posts_add",
                     view_renderer="string",)
    config.add_route("del_post_delete", "/delapi/posts/delete",
                     view="bookie.views.delapi.posts_delete",
                     view_renderer="string",)
    config.add_route("del_post_get", "/delapi/posts/get",
                     view="bookie.views.delapi.posts_get",
                     view_renderer="/delapi/posts_get.mako",)
    config.add_route("del_tag_complete", "/delapi/tags/complete",
                     view="bookie.views.delapi.tags_complete",
                     view_renderer="/delapi/tags_complete.mako",)

    # bmark routes
    config.add_route("bmark_popular", "/popular",
                     view="bookie.views.bmarks.popular",
                     view_renderer="/bmark/popular.mako",)
    config.add_route("bmark_popular_page", "/popular/{page}",
                     view="bookie.views.bmarks.popular",
                     view_renderer="/bmark/popular.mako",)

    config.add_route("bmark_recent", "/recent",
                     view="bookie.views.bmarks.recent",
                     view_renderer="/bmark/recent.mako",)
    config.add_route("bmark_recent_page", "/recent/{page}",
                     view="bookie.views.bmarks.recent",
                     view_renderer="/bmark/recent.mako",)

    config.add_route("bmark_delete", "/bmark/delete",
                     view="bookie.views.bmarks.delete",)
    config.add_route("bmark_confirm_delete", "/bmark/confirm/delete/{bid}",
                     view="bookie.views.bmarks.confirm_delete",
                     view_renderer="/bmark/confirm_delete.mako",)
    config.add_route("bmark_readable", "/bmark/readable/{hash_id}",
                     view="bookie.views.bmarks.readable",
                     view_renderer="/bmark/readable.mako",)


    # tag related routes
    config.add_route("tag_list", "/tags",
                     view="bookie.views.tags.tag_list",
                     view_renderer="/tag/list.mako",)

    config.add_route("tag_bmarks_ajax", "/tags/*tags",
                     view="bookie.views.tags.bmark_list",
                     xhr=True,
                     view_renderer="morjson",)
    config.add_route("tag_bmarks", "/tags/*tags",
                     view="bookie.views.tags.bmark_list",
                     view_renderer="/tag/bmarks_wrap.mako",)

    config.add_route("import", "/import",
                     view="bookie.views.utils.import_bmarks",
                     view_renderer="/utils/import.mako",)


    config.add_route("search", "/search",
                     view="bookie.views.utils.search",
                     view_renderer="/utils/results_wrap.mako",)

    # matches based on the header
    # HTTP_X_REQUESTED_WITH
    config.add_route("search_ajax", "/search*terms",
                     view="bookie.views.utils.search",
                     xhr=True,
                     view_renderer="morjson",)

    config.add_route("search_rest", "/search*terms",
                     view="bookie.views.utils.search",
                     view_renderer="/utils/results_wrap.mako",)

    config.add_route("export", "/export",
                     view="bookie.views.utils.export",
                     view_renderer="/utils/export.mako",)


    config.add_route("redirect", "/redirect/{hash_id}",
                     view="bookie.views.utils.redirect")

    return config
