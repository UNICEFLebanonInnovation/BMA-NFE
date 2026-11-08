"""Private child-photo access and deployment health for MEHE."""
from pathlib import PurePosixPath
from urllib.parse import quote
import mimetypes

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import storages
from django.db import DatabaseError, connection
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_safe

from student_registration.child.models import Child
from student_registration.mscc.models import Registration

def can_view_photo(user, child):
    if not user.is_active:
        return False
    if user.is_superuser or (user.is_staff and user.has_perm('child.view_child')):
        return True
    groups = set(user.groups.values_list('name', flat=True))
    registrations = Registration.objects.filter(child=child, deleted=False)
    if 'MSCC_MEHE' in groups:
        return registrations.exists()
    if 'MSCC_PARTNER' in groups and user.partner_id:
        return registrations.filter(partner_id=user.partner_id).exists()
    if 'MSCC_CENTER' in groups and user.center_id:
        return registrations.filter(center_id=user.center_id).exists()
    return False

@require_safe
@login_required
def child_photo(request, name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or '\x00' in name:
        raise Http404
    if path.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp'):
        raise Http404
    child = Child.objects.filter(photo=name).first()
    if child is None or not can_view_photo(request.user, child):
        raise Http404
    storage = child.photo.storage
    try:
        if not storage.exists(name):
            raise Http404
        if getattr(settings, 'NFE_MEDIA_X_ACCEL_REDIRECT', False):
            response = HttpResponse(content_type=mimetypes.guess_type(name)[0] or 'application/octet-stream')
            response['X-Accel-Redirect'] = '/_nfe_private_media/' + quote(name, safe='/')
        else:
            response = FileResponse(storage.open(name, 'rb'), content_type=mimetypes.guess_type(name)[0])
    except OSError:
        return HttpResponse('Photo storage is temporarily unavailable', status=503)
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

@require_safe
def readiness(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        storages['default'].check_available()
    except (DatabaseError, OSError, AttributeError):
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})
