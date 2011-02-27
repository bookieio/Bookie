"""Create routes here and gets returned into __init__ main()"""


def build_routes(config):
    """Add any routes to the config"""

    config.add_route("home", "/", view="bookie.views.my_view",
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

    config.add_route("bmark_recent", "/recent",
                     view="bookie.views.bmarks.recent",
                     view_renderer="/bmark/recent.mako",)
    config.add_route("bmark_recent_page", "/recent/{page}",
                     view="bookie.views.bmarks.recent",
                     view_renderer="/bmark/recent.mako",)

    config.add_route("tag_list", "/tags",
                     view="bookie.views.tags.list",
                     view_renderer="/tag/list.mako",)
    config.add_route("tag_bmarks", "/tags/{tag}",
                     view="bookie.views.tags.bmark_list",
                     view_renderer="/tag/bmarks.mako",)
    config.add_route("tag_bmarks_page", "/tags/{tag}/{page}",
                     view="bookie.views.tags.bmark_list",
                     view_renderer="/tag/bmarks.mako",)


    return config
