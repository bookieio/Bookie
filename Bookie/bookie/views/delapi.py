from bookie.models import DBSession, NoResultFound
from bookie.models import Bmark, BmarkMgr


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


def posts_delete(request):
    """Remove a bmark from the system"""
    params = request.GET

    if 'url' in params and params['url']:
        try:
            bmark = BmarksMgr.get(params['url'])

            session = DBSession()
            session.delete(bmark)

            return '<result code="done" />'

        except NoResultFound:
            # if it's not found, then there's not a bookmark to delete
            return '<result code="Bad Request: bookmark not found" />'
