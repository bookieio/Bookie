from bookie.models import DBSession
from bookie.models import MyModel

def my_view(request):
    dbsession = DBSession()
    root = dbsession.query(MyModel).filter(MyModel.name==u'root').first()

    return {'root':root, 'project':'Bookie'}


def rick(request):
    return {}

def rickme(request):
    rdict = request.matchdict
    sometext = rdict['sometext']
    return {'display': sometext}
