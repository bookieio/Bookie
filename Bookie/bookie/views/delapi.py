from bookie.models import DBSession
from bookie.models import Bmark

def posts_add(request):

    params = request.GET

    if 'url' in params and params['url']:
        # then let's store this thing
        mark = Bmark(params['url'],
                     desc=params['description'],
                     ext=params['extended'],
                     tags=params['tags'],
               )
        session = DBSession()
        session.add(mark)
        return '<result code="done" />'
    else:
        return '<result code="Bad Request: missing url" />'
