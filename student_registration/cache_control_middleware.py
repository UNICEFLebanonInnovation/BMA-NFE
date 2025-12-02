from django.http import HttpRequest, HttpResponse


class CacheControlMiddleware:
    """Prevent caching of secure pages to reduce risk of stale auth data."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if request.is_secure:
            response["Cache-Control"] = "no-cache"

        return response
