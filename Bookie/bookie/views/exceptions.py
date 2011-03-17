def resource_not_found(exc, request):
    """Display a custom 404 page when the HTTPNotFound fired"""
    request.status_string = "404 Not Found"
    request.status = 404
    return {'message': str(exc)}

def resource_forbidden(exc, request):
    """Display a custom 403 page when the HTTPForbidden fired"""
    request.status_string = "403 Forbidden"
    request.status = 403
    return {'message': str(exc)}
