# middleware/user_activity.py
import json
import logging

from django.utils.deprecation import MiddlewareMixin

from student_registration.backends.models import UserActivity

logger = logging.getLogger(__name__)


class UserActivityMiddleware(MiddlewareMixin):
    """Middleware to log user activity for authenticated users."""

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def _extract_data(self, request):
        if request.method in {"POST", "PUT", "PATCH"}:
            content_type = request.META.get("CONTENT_TYPE", "").lower()
            if "application/json" in content_type:
                try:
                    body = request.body.decode(request.encoding or "utf-8")
                    return json.loads(body)
                except Exception:  # pragma: no cover - fall back to POST
                    return {}
            return request.POST.copy()
        return request.GET.copy()

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if request.user.is_authenticated and not request.path.startswith("/admin"):
                data = self._extract_data(request)
                if hasattr(data, "lists"):
                    data_dict = dict(data.lists())
                else:
                    data_dict = data

                data_dict.update(
                    {
                        "ip": request.META.get("REMOTE_ADDR"),
                        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    }
                )

                serialized_data = json.dumps(data_dict)

                UserActivity.objects.create(
                    username=request.user.username,
                    path=request.get_full_path(),
                    method=request.method,
                    data=serialized_data,
                )
        except Exception as e:  # pragma: no cover - logging should not break request
            logger.exception(e)

        return response
