class HSTSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.is_secure:
            response['Strict-Transport-Security'] = 'max-age=2592000; includeSubdomains'

        return response
