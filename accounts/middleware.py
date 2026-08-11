"""Middleware that tracks the current request user for the audit service."""

from accounts import audit


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        audit.set_current_user(getattr(request, "user", None))
        try:
            return self.get_response(request)
        finally:
            audit.set_current_user(None)
