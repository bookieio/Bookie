"""View callables for utilities like bookmark imports, etc"""
import logging


def import_bmarks(request):
    """Allow users to upload a delicious bookmark export"""
    data = {}
    request.session.flash("Error something")

    msg = request.session.pop_flash()

    if msg:
        data['error'] = msg
    else:
        data['error'] = None

    return data

