import logging

from pyramid.renderers import render_to_response
from pyramid.view import view_config

LOG = logging.getLogger()


@view_config(route_name="tests")
def jstest(request):
    """Display a js test html file"""
    rdict = request.matchdict
    LOG.debug('TESTS')
    LOG.debug(rdict)
    LOG.debug(rdict.get('file'))

    tpl_file = "/tests/{0}.mako".format(rdict.get('file'))
    LOG.debug(tpl_file)

    return render_to_response(tpl_file, {}, request=request)
