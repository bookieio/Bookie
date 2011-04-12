"""Create routes here and gets returned into __init__ main()"""
from pyramid.exceptions import NotFound
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden
from bookie.views.exceptions import resource_not_found
from bookie.views.exceptions import resource_forbidden


def build_routes(config):
    """Add any routes to the config"""

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
    config.add_route("tag_bmarks", "/tags/{tag}",
                     view="bookie.views.tags.bmark_list",
                     view_renderer="/tag/bmarks.mako",)
    config.add_route("tag_bmarks_page", "/tags/{tag}/{page}",
                     view="bookie.views.tags.bmark_list",
                     view_renderer="/tag/bmarks.mako",)

    config.add_route("import", "/import",
                     view="bookie.views.utils.import_bmarks",
                     view_renderer="/utils/import.mako",)

    config.add_route("search", "/search",
                     view="bookie.views.utils.search",
                     view_renderer="/utils/results.mako",)

    config.add_route("export", "/export",
                     view="bookie.views.utils.export",
                     view_renderer="/utils/export.mako",)

    config.add_route("redirect", "/redirect/{hash_id}",
                     view="bookie.views.utils.redirect")

    return config
