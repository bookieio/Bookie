"""Create routes here and gets returned into __init__ main()"""


def build_routes(config):
    """Add any routes to the config"""

    config.add_route('home', '/', view='bookie.views.my_view',
                     view_renderer='/testmako.mako')
    config.add_route('rick', '/rick', view='bookie.views.rick',
                    view_renderer='/testmako.mako')
    config.add_route('rick_index', '/rick/', view='bookie.views.rick',
                    view_renderer='/testmako.mako')

    config.add_route('rick_2',
                     '/rick/{sometext}',
                     view='bookie.views.rickme',
                     view_renderer='/rick.mako')

    return config
