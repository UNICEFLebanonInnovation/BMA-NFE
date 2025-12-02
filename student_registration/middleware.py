from datetime import datetime, timedelta
from typing import Optional

from django.conf import settings
from django.contrib import auth
from django.http import HttpRequest, HttpResponse


class AutoLogout:
    """Expire authenticated sessions that have been idle for too long."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Refresh or expire the session before handing off to the view."""

        self._enforce_session_timeout(request)
        return self.get_response(request)

    def _enforce_session_timeout(self, request: HttpRequest) -> None:
        """Logout authenticated users whose session has exceeded the idle limit."""

        if not request.user.is_authenticated:
            return

        last_touch = self._get_last_touch(request)
        if last_touch is None:
            # No usable timestamp was found; start tracking from now.
            self._set_last_touch(request)
            return

        if self._is_inactive(last_touch):
            auth.logout(request)
            request.session.flush()
            return

        self._set_last_touch(request)

    def _get_last_touch(self, request: HttpRequest) -> Optional[datetime]:
        """Return the stored timestamp of the user's last activity, if valid."""

        last_touch_str = request.session.get("last_touch")
        if not last_touch_str:
            return None

        try:
            return datetime.fromisoformat(last_touch_str)
        except ValueError:
            # Invalid date format — remove it so tracking can restart cleanly.
            request.session.pop("last_touch", None)
            return None

    def _is_inactive(self, last_touch: datetime) -> bool:
        """Check whether the stored timestamp exceeds the configured idle limit."""

        idle_duration = datetime.now() - last_touch
        allowed_idle_time = timedelta(minutes=settings.AUTO_LOGOUT_DELAY)
        return idle_duration > allowed_idle_time

    def _set_last_touch(self, request: HttpRequest) -> None:
        """Persist the current timestamp to track future inactivity."""

        request.session["last_touch"] = datetime.now().isoformat()
