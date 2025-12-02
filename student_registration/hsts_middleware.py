from django.http import HttpRequest, HttpResponse


class HSTSMiddleware:
    """Apply an HSTS header to secure requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if request.is_secure:
            response["Strict-Transport-Security"] = "max-age=2592000; includeSubdomains"

        return response
