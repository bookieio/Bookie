"""View callables for utilities like bookmark imports, etc"""
import logging
from pyramid.httpexceptions import HTTPFound

from bookie.lib.importer import DelImporter
from bookie.lib.access import Authorize

LOG = logging.getLogger(__name__)

def import_bmarks(request):
    """Allow users to upload a delicious bookmark export"""
    data = {}
    post = request.POST

    if post:
        # we have some posted values
        with Authorize(request.registry.settings.get('api_key', ''),
                       post.get('api_key', None)):

            # if auth fails, it'll raise an HTTPUnauthorized exception
            files = post.get('import_file', None)

            if files is not None:
                # upload is there for use
                # process the file using the import script
                importer = DelImporter(files.file)
                importer.process()

                # @todo get a count of the imported bookmarks and setup a flash
                # message. Forward to / and display the import message

                # request.session.flash("Error something")
                return HTTPFound(location=request.route_url('home'))
            else:
                msg = request.session.pop_flash()

                if msg:
                    data['error'] = msg
                else:
                    data['error'] = None

            return data
    else:
        # just display the form
        return {}
