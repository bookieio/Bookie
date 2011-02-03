"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper


def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    map.connect('/login', controller='accounts', action='login')
    map.connect('/post_login', controller='accounts', action='post_login')

    map.connect('/accounts/fetch_ldap_user/{user_name}', controller='accounts', action='fetch_ldap_user')
    map.connect('/accounts/{user_name}/{action}', controller='accounts')


    map.connect('/page/{page_slug}', controller='qcontent', action='render_page')
    map.connect('/layout/{page_id}', controller='qcontent', action='render_layout')
    map.connect('/section/{section_id}', controller='qcontent', action='render_section')

    map.connect('/{controller}/admin/{slug}', controller="qcontent", action="admin_page")

    map.connect('/{controller}/page/new', controller="qcontent", action="admin_page_new")
    map.connect('/{controller}/{slug}/edit', controller="qcontent", action="admin_page_edit")
    map.connect('/{controller}/{slug}/delete', controller="qcontent", action="admin_page_delete")
    map.connect('/{controller}/{slug}/layout/preview', controller="qcontent", action="layout_preview")
    map.connect('/{controller}/{slug}/layout/{layout_part}', controller="qcontent", action="layout_load")
    map.connect('/{controller}/{slug}/reorder', controller="qcontent", action="reorder")
    map.connect('/{controller}/{slug}/new_section', controller="qcontent", action="section_new")

    map.connect('/{controller}/layout/list', controller="qcontent", action="layout_list")

    map.connect('/{controller}/section/{section_id}/edit', controller="qcontent", action="section_edit")
    map.connect('/{controller}/section/{section_id}/delete', controller="qcontent", action="section_delete")


    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')
    map.connect('/', controller='accounts', action='login')

    return map
