from .auth_logging import assign_request_id


class RequestIdMiddleware:
    """Ensure each request has a correlation id for structured logs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = assign_request_id(request)
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        return response
