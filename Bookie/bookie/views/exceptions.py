def resource_not_found(exc, request):
    """Display a custom 404 page when the HTTPNotFound fired"""
    return {'message': str(exc)}

def resource_forbidden(exc, request):
    """Display a custom 403 page when the HTTPForbidden fired"""
    return {'message': str(exc)}
