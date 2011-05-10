"""Custom methods to handle 404 and 403 exceptions

These are hooked into the routes and provide a means for displaying a custom
handler that runs through a mako template. It should allow us to have pretty
themed 404/403 pages

"""


def resource_not_found(exc, request):
    """Display a custom 404 page when the HTTPNotFound fired"""
    request.response_status = "404 Not Found"
    return {'message': str(exc)}

def resource_forbidden(exc, request):
    """Display a custom 403 page when the HTTPForbidden fired"""
    request.response_status = "403 Forbidden"
    return {'message': str(exc)}
