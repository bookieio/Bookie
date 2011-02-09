"""Create routes here and gets returned into __init__ main()"""


def build_routes(config):
    """Add any routes to the config"""

    config.add_route("home", "/", view="bookie.views.my_view",
                     view_renderer="/testmako.mako")


    # DELAPI Routes
    config.add_route("del_post_add", "/delapi/posts/add",
                     view="bookie.views.delapi.posts_add",
                     view_renderer="string")

    # config.add_route("rick_2",
    #                  "/rick/{sometext}",
    #                  view="bookie.views.rickme",
    #                  view_renderer="/rick.mako")


    return config
