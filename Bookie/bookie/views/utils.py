"""View callables for utilities like bookmark imports, etc"""
import logging

from bookie.lib.importer import DelImporter

LOG = logging.getLogger(__name__)

def import_bmarks(request):
    """Allow users to upload a delicious bookmark export"""
    data = {}

    post = request.POST
    files = post.get('import_file', None)

    if files is not None:
        # upload is there for use
        # process the file using the import script

        importer = DelImporter(files.file)
        importer.process()

        # request.session.flash("Error something")

    else:
        msg = request.session.pop_flash()

        if msg:
            data['error'] = msg
        else:
            data['error'] = None

    return data
