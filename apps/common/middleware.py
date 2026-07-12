import uuid

import structlog


class RequestIDMiddleware:
    """Bind a per-request ID to structlog context and echo it in the response header.

    Accepts an inbound X-Request-ID (useful behind a proxy that already
    minted one) or generates a new one. This is what makes a user-reported
    error findable in the logs.
    """

    header_name = "X-Request-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = self.get_response(request)
        response[self.header_name] = request_id
        return response
