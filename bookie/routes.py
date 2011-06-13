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

    # auth routes
    config.add_route("index", "/")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")

    # DELAPI Routes
    # config.add_route("del_post_add", "/{username}/delapi/posts/add")
    # config.add_route("del_post_delete", "/{username}/delapi/posts/delete")
    # config.add_route("del_post_get", "/{username}/delapi/posts/get")
    # config.add_route("del_tag_complete", "/{username}/delapi/tags/complete")

    # bmark routes
    config.add_route("bmark_recent", "/recent")
    config.add_route("bmark_recent_tags", "/recent/*tags")

    config.add_route("bmark_popular", "/popular")
    config.add_route("bmark_popular_tags", "/popular/*tags")
    config.add_route("bmark_readable", "/bmark/readable/{hash_id}")

    # user based bmark routes
    config.add_route("user_bmark_recent", "/{username}/recent")
    config.add_route("user_bmark_recent_tags", "/{username}/recent/*tags")

    config.add_route("user_bmark_popular", "/{username}/popular")
    config.add_route("user_bmark_popular_tags", "/{username}/popular/*tags")

    # config.add_route("bmark_delete", "/bmark/delete")
    # config.add_route("bmark_confirm_delete", "/bmark/confirm/delete/{bid}")

    # tag related routes
    config.add_route("tag_list", "/tags")
    # config.add_route("tag_bmarks_ajax", "/tags/*tags", xhr=True)
    # config.add_route("tag_bmarks", "/tags/*tags")

    # user tag related
    config.add_route("user_tag_list", "/{username}/tags")
    # config.add_route("tag_bmarks_ajax", "/{username}/tags/*tags", xhr=True)
    # config.add_route("tag_bmarks", "/{username}/tags/*tags")
    # config.add_route("user_tag_bmarks", "/{username}/tags/*tags")

    config.add_route("user_import", "/{username}/import")
    # config.add_route("search", "/search")
    # config.add_route("search_results", "/results")
    # config.add_route("user_search", "/{username}/search")
    # config.add_route("search_results", "/{username}/results")

    # matches based on the header
    # HTTP_X_REQUESTED_WITH
    # config.add_route("search_results_ajax", "/results*terms", xhr=True)
    # config.add_route("search_results_rest", "/results*terms")

    # removed the overall export. We're not going to have a link for exporting
    # all in one swoop. It'll kill things
    # config.add_route("user_export", "/{username}/export")

    config.add_route("redirect", "/redirect/{hash_id}")
    # config.add_route("user_redirect", "/{username}/redirect/{hash_id}")

    # # MOBILE routes
    # config.add_route("mobile", "/m")
    # config.add_route("user_mobile", "/{username}/m")

    # API
    # config.add_route('api_bmark_recent', '/api/v1/bmarks/recent')
    # config.add_route('api_bmark_popular', '/api/v1/bmarks/popular')
    # config.add_route("api_bmark_search", "/api/v1/bmarks/search/*terms")

    # config.add_route("user_api_bmark_recent", "/{username}/api/v1/bmarks/recent")
    # config.add_route("user_api_bmark_popular", "/{username}/api/v1/bmarks/popular")
    # config.add_route("user_api_bmark_search", "/{username}/api/v1/bmarks/search/*terms")
    # config.add_route("user_api_bmark_sync", "/{username}/api/v1/bmarks/sync")
    # config.add_route("user_api_bmark_add", "/{username}/api/v1/bmarks/add")
    # config.add_route("user_api_bmark_remove", "/{username}/api/v1/bmarks/remove")

    # # this route must be last, none of the above will look like hashes (22char)
    # # so it's safe to have as a kind of default route at the end
    # config.add_route("api_bmark_hash", "/api/v1/bmarks/{hash_id}")
    # config.add_route("user_api_bmark_hash", "/{username}/api/v1/bmarks/{hash_id}")

    # # api calls for tag relation information
    # config.add_route("api_tag_complete", "/api/v1/tags/complete")
    # config.add_route("user_api_tag_complete", "/api/v1/tags/complete")

    return config
