def resource_not_found(exc, request):
    """Display a custom 404 page when the HTTPNotFound fired"""
    request.response_status= "404 Not Found"
    return {'message': str(exc)}

def resource_forbidden(exc, request):
    """Display a custom 403 page when the HTTPForbidden fired"""
    request.response_status = "403 Forbidden"
    return {'message': str(exc)}
