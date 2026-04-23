
import json
import datetime
import os
import io
import re
import logging

from pathlib import Path
from time import mktime

from django.http import FileResponse, HttpResponse
from storages.backends.azure_storage import AzureStorage

logger = logging.getLogger(__name__)


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

    def decode(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


class ExportStorage(AzureStorage):
    """Azure storage backend dedicated for exported files."""
    location = "export"


def download_file(file_name, returned_file_name, content_type="application/octet-stream", delete_after=True):
    """Retrieve a file from Azure storage and return it as an HTTP response."""

    storage = ExportStorage()
    try:
        with storage.open(file_name, "rb") as fh:
            file_stream = io.BytesIO(fh.read())
            file_stream.seek(0)
            response = FileResponse(file_stream, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{returned_file_name}"'
    except Exception as exc:  # pragma: no cover - logged for debugging purposes
        logger.exception("Error reading file %s", file_name)
        response = HttpResponse(f"Error reading file: {exc}")
    # if delete_after:
    #     storage.delete(file_name)
    return response


def is_valid_filename(filename, extension):
    pattern = rf'^[a-zA-Z0-9-_]+\.{extension}$'
    return re.match(pattern, filename) is not None


def send_push_to_web_0(user, title, body, data=None):
    """Send a web push notification via Firebase Cloud Messaging.

    Parameters
    ----------
    user: ``django.contrib.auth.models.User``
        Recipient of the notification. All tokens stored for this user will
        receive the message.
    title: str
        Title shown in the web push notification.
    body: str
        Body text of the notification.
    data: dict, optional
        Extra data to include in the notification payload. Values are
        converted to strings as required by FCM.

    Returns
    -------
    bool
        ``True`` when at least one message has been successfully sent,
        otherwise ``False``.
    """

    # Import locally to avoid loading heavy dependencies when unused.
    from pathlib import Path

    import firebase_admin
    from firebase_admin import credentials, messaging

    from student_registration.users.models import WebPushToken

    # Collect all tokens registered for the user.
    tokens = list(
        WebPushToken.objects.filter(user=user).values_list("token", flat=True)
    )
    if not tokens:
        return False

    # Initialise the Firebase app if this hasn't happened yet.  The
    # credentials file lives in ``utility/firebase-creds.json`` relative to the
    # project root.
    if not firebase_admin._apps:  # pragma: no cover - simple initialisation
        project_root = Path(__file__).resolve().parents[2]
        cred_path = project_root / "utility" / "firebase-creds.json"
        cred = credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred)

    # FCM requires payload data values to be strings.
    payload_data = {k: str(v) for k, v in (data or {}).items()}

    message = messaging.MulticastMessage(
        tokens=tokens,
        notification=messaging.Notification(title=title, body=body),
        data=payload_data,
    )

    # Send the notification to all tokens.
    response = messaging.send_each_for_multicast(message)
    return response.success_count > 0


def send_push_to_web(user, title, body, data=None):
    import firebase_admin
    from firebase_admin import credentials, messaging

    from student_registration.users.models import WebPushToken

    root_dirt = Path(__file__).parents[2]
    FIREBASE_CREDENTIALS_FILE = os.path.join(str(root_dirt / "utility"), 'firebase-creds.json')
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE)
    # firebase_app = firebase_admin.initialize_app(cred)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    tokens = list(WebPushToken.objects.filter(user=user).values_list("token", flat=True))
    if not tokens:
        logger.warning("No WebPushTokens found for user %s", user)
        return False

    payload_data = {str(k): str(v) for k, v in (data or {}).items()}

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        webpush=messaging.WebpushConfig(
            headers={"Urgency": "high"},
            notification=messaging.WebpushNotification(
                title=title,
                body=body,
                icon="/static/images/logo.png",
            ),
        ),
        tokens=tokens,
        data=payload_data,
    )
    try:
        response = messaging.send_each_for_multicast(message)
        return response.success_count > 0
    except Exception as e:
        logger.exception("Error Sending Push notifications: %s", e)
        return False
