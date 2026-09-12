# -*- coding: utf-8 -*-
"""REST endpoints of the mobile synchronisation API (``/api/mobile/v1/``)."""
from __future__ import unicode_literals

import logging

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from . import access, serialization
from .engine import PushEngine, batch_report, validate_batch_payload
from .models import MobileDevice, MobileSyncBatch
from .registry import (
    KIND_ATTENDANCE, KIND_TEACHER_ATTENDANCE, get_registry, specs_for_user,
)
from .schema import build_schemas

logger = logging.getLogger(__name__)


def _device(user, request_data):
    device_id = (request_data or {}).get('device_id')
    if not device_id:
        return None
    device, _ = MobileDevice.objects.get_or_create(user=user, device_id=str(device_id)[:128])
    changed = []
    name = (request_data or {}).get('device_name')
    version = (request_data or {}).get('app_version')
    if name and device.name != name:
        device.name = str(name)[:255]
        changed.append('name')
    if version and device.app_version != version:
        device.app_version = str(version)[:64]
        changed.append('app_version')
    if changed:
        device.save(update_fields=changed + ['modified'])
    return device


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''
        if not username or not password:
            return Response({'detail': 'username and password are required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid username or password.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'detail': 'This account is inactive.'}, status=status.HTTP_403_FORBIDDEN)
        token, _ = Token.objects.get_or_create(user=user)
        device = _device(user, request.data)
        if device is not None:
            device.last_login = timezone.now()
            device.save(update_fields=['last_login', 'modified'])
        return Response({
            'token': token.key,
            'server_time': timezone.now().isoformat(),
            'user': access.user_profile(user),
        })


class MobileAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class LogoutView(MobileAPIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'status': 'ok'})


class MeView(MobileAPIView):
    def get(self, request):
        return Response({'user': access.user_profile(request.user),
                         'server_time': timezone.now().isoformat()})


class BootstrapView(MobileAPIView):
    """Reference data, choice lists and form schemas for offline work."""

    def get(self, request):
        user = request.user
        _device(user, request.query_params)
        return Response({
            'server_time': timezone.now().isoformat(),
            'user': access.user_profile(user),
            'reference': reference_data(user),
            'choices': attendance_choices(),
            'schemas': build_schemas(user),
            'entities': [spec.key for spec in specs_for_user(user)],
        })


def _rows(queryset, *fields):
    return list(queryset.values(*fields))


def reference_data(user):
    from student_registration.alp.models import ALPGradingDefinition, ALPProgram, ALPRound
    from student_registration.clm.models import Disability
    from student_registration.locations.models import Center, Location
    from student_registration.mscc.models import Packages, Round
    from student_registration.schools.models import (
        CLMRound, ClubType, EducationalLevel, PartnerOrganization, School, Section,
    )
    from student_registration.students.models import AttachmentType, IDType, Nationality, Training
    from .registry import clm_school_ids, mscc_center_ids

    caps = access.module_capabilities(user)

    schools = School.objects.none()
    if caps['alp']['enabled'] and user.school_id:
        schools = schools | School.objects.filter(id=user.school_id)
    if caps['clm']['enabled']:
        schools = schools | School.objects.filter(id__in=clm_school_ids(user))
    if caps['mscc']['enabled']:
        schools = schools | School.objects.filter(is_bma=True)
    if user.school_id:
        schools = schools | School.objects.filter(id=user.school_id)

    centers = Center.objects.none()
    if caps['mscc']['enabled']:
        centers = Center.objects.filter(id__in=mscc_center_ids(user))
    if user.center_id:
        centers = centers | Center.objects.filter(id=user.center_id)

    return {
        'nationalities': _rows(Nationality.objects.order_by('id'), 'id', 'name', 'name_en', 'code'),
        'id_types': _rows(IDType.objects.filter(active=True).order_by('id'), 'id', 'name'),
        'disabilities': _rows(Disability.objects.filter(active=True).order_by('name'), 'id', 'name', 'name_en'),
        'education_levels': _rows(EducationalLevel.objects.order_by('id'), 'id', 'name'),
        'trainings': _rows(Training.objects.order_by('name'), 'id', 'name'),
        'attachment_types': _rows(AttachmentType.objects.order_by('name'), 'id', 'name'),
        'club_types': _rows(ClubType.objects.order_by('id'), 'id', 'name'),
        'sections': _rows(Section.objects.order_by('id'), 'id', 'name'),
        'locations': [
            {'id': l['id'], 'name': l['name'], 'name_en': l['name_en'], 'type': l['type__name'],
             'level': l['level'], 'parent_id': l['parent_id'], 'p_code': l['p_code']}
            for l in Location.objects.order_by('tree_id', 'lft').values(
                'id', 'name', 'name_en', 'type__name', 'level', 'parent_id', 'p_code')
        ],
        'partners': _rows(PartnerOrganization.objects.order_by('name'), 'id', 'name', 'short_name', 'active'),
        'centers': [
            {**c, 'partner_id': c.pop('partner_id')} for c in centers.distinct().order_by('name').values(
                'id', 'name', 'partner_id', 'governorate_id', 'caza_id', 'cadaster_id', 'type',
                'programs', 'provided_packages', 'is_active', 'latitude', 'longitude')
        ],
        'schools': _rows(schools.distinct().order_by('number'), 'id', 'number', 'name', 'type',
                         'governorate_id', 'district_id', 'cadaster_id', 'is_bma', 'is_closed',
                         'working_days', 'weekend', 'latitude', 'longitude'),
        'rounds': {
            'mscc': _rows(Round.objects.order_by('name'), 'id', 'name', 'current_year', 'year'),
            'alp': _rows(ALPRound.objects.order_by('name'), 'id', 'name', 'current_year'),
            'clm': _rows(CLMRound.objects.order_by('name'), 'id', 'name', 'current_year',
                         'current_round_bridging', 'start_date_bridging', 'end_date_bridging'),
        },
        'alp_programs': _rows(ALPProgram.objects.order_by('name'), 'id', 'name'),
        'alp_grading_definitions': _rows(ALPGradingDefinition.objects.order_by('material'),
                                         'id', 'material', 'min_grade', 'max_grade'),
        'packages': _rows(Packages.objects.order_by('id'), 'id', 'name', 'type', 'category',
                          'required', 'min_age', 'max_age'),
    }


def _choice_list(choices):
    return [{'value': '' if v is None else str(v), 'label': str(l)} for v, l in choices]


def attendance_choices():
    from student_registration.alp.models import ALPAttendance, ALPAttendanceChild, ALPTeacherAttendance
    from student_registration.attendances.models import (
        CLMAttendance, CLMAttendanceStudent, MSCCAttendance, MSCCAttendanceChild,
    )
    from student_registration.clm.models import Bridging
    from student_registration.mscc.models import EducationService
    from student_registration.child.models import Child
    return {
        'mscc.attendance.education_program': _choice_list(MSCCAttendance.EDUCATION_PROGRAM),
        'mscc.education_service.education_program': _choice_list(EducationService.EDUCATION_PROGRAM),
        'mscc.attendance.class_section': _choice_list(EducationService.CLASS_SECTION),
        'mscc.attendance.absence_reason': _choice_list(MSCCAttendanceChild.ABSENCE_REASON),
        'mscc.attendance.close_reason': _choice_list(MSCCAttendance.CLOSE_REASON),
        'alp.attendance.absence_reason': _choice_list(ALPAttendanceChild.ABSENCE_REASON),
        'alp.attendance.close_reason': _choice_list(ALPAttendance.CLOSE_REASON) + [
            {'value': 'Other', 'label': 'Other'}],
        'alp.teacher_attendance.status': _choice_list(
            getattr(ALPTeacherAttendance, 'STATUS', (('Present', 'Present'), ('Absent', 'Absent')))),
        'clm.attendance.registration_level': _choice_list(Bridging.REGISTRATION_LEVEL),
        'clm.attendance.absence_reason': [
            {'value': '', 'label': '----------'}, {'value': 'Sick', 'label': 'Sick'},
            {'value': 'Transportation', 'label': 'Transportation'}, {'value': 'Other', 'label': 'Other'}],
        'clm.attendance.close_reason': _choice_list(CLMAttendance.CLOSE_REASON)
        if hasattr(CLMAttendance, 'CLOSE_REASON') else [],
        'child.gender': _choice_list(Child.GENDER),
        'yes_no': _choice_list(Child.YES_NO),
    }


class PullView(MobileAPIView):
    """Incremental download of the records visible to the user."""

    def get(self, request):
        user = request.user
        since_raw = request.query_params.get('since')
        since = parse_datetime(since_raw) if since_raw else None
        if since_raw and since is None:
            return Response({'detail': 'since must be an ISO-8601 datetime.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if since is not None and timezone.is_aware(since):
            since = timezone.make_naive(since, timezone.get_default_timezone()) \
                if not timezone.is_aware(timezone.now()) else since
        try:
            cursor = int(request.query_params.get('cursor') or 0)
            limit = min(int(request.query_params.get('limit') or 500), 2000)
        except ValueError:
            return Response({'detail': 'cursor and limit must be integers.'},
                            status=status.HTTP_400_BAD_REQUEST)
        wanted = request.query_params.get('entities')
        wanted = set(w.strip() for w in wanted.split(',') if w.strip()) if wanted else None
        server_time = timezone.now()

        specs = [s for s in specs_for_user(user) if s.pullable and (wanted is None or s.key in wanted)]
        changes = []
        skipped = 0
        remaining = limit
        has_more = False
        for spec in specs:
            if remaining <= 0:
                has_more = True
                break
            rows = self._changes_for(spec, user, since)
            for change in rows:
                if skipped < cursor:
                    skipped += 1
                    continue
                if remaining <= 0:
                    has_more = True
                    break
                changes.append(change)
                remaining -= 1
            if has_more:
                break

        device = _device(user, request.query_params)
        if device is not None and not has_more:
            device.last_pull = server_time
            device.save(update_fields=['last_pull', 'modified'])
        return Response({
            'server_time': server_time.isoformat(),
            'since': since_raw,
            'changes': changes,
            'next_cursor': str(cursor + len(changes)) if has_more else None,
            'has_more': has_more,
        })

    def _changes_for(self, spec, user, since):
        if spec.kind == KIND_ATTENDANCE:
            return self._attendance_changes(spec, user, since)
        if spec.kind == KIND_TEACHER_ATTENDANCE:
            return self._teacher_attendance_changes(spec, user, since)
        qs = spec.scope(user) if spec.scope else spec.model.objects.none()
        if since is not None and spec.has_modified:
            qs = qs.filter(modified__gte=since)
        qs = qs.order_by('pk')
        if spec.identity:
            qs = qs.select_related(spec.person_field)
        results = []
        for obj in qs.iterator():
            if spec.identity:
                data = serialization.serialize_registration(obj, spec)
            else:
                data = serialization.serialize_instance(obj)
            results.append({
                'entity': spec.key,
                'server_id': obj.pk,
                'parent_id': getattr(obj, spec.parent_field + '_id', None) if spec.parent else None,
                'modified': data.get('modified'),
                'deleted': bool(getattr(obj, 'deleted', False)),
                'data': data,
            })
        return results

    def _attendance_changes(self, spec, user, since):
        qs = spec.scope(user)
        child_rel = 'attendance_student' if spec.key == 'clm.attendance_day' else 'attendance_child'
        if since is not None:
            qs = qs.filter(Q(modified__gte=since) | Q(**{child_rel + '__modified__gte': since})).distinct()
        qs = qs.order_by('pk').prefetch_related(child_rel)
        serializer = {
            'mscc.attendance_day': serialization.serialize_mscc_attendance,
            'alp.attendance_day': serialization.serialize_alp_attendance,
            'clm.attendance_day': serialization.serialize_clm_attendance,
        }[spec.key]
        results = []
        for day in qs:
            data = serializer(day)
            results.append({
                'entity': spec.key, 'server_id': day.pk, 'parent_id': None,
                'modified': day.modified.isoformat() if day.modified else None,
                'deleted': False, 'data': data,
            })
        return results

    def _teacher_attendance_changes(self, spec, user, since):
        qs = spec.scope(user)
        if since is not None:
            dates = qs.filter(modified__gte=since).values_list('date', flat=True).distinct()
            qs = spec.scope(user).filter(date__in=list(dates))
        qs = qs.order_by('date', 'teacher_id')
        grouped = {}
        for row in qs:
            grouped.setdefault(row.date, []).append(row)
        results = []
        for date, rows in sorted(grouped.items(), key=lambda kv: (kv[0] is None, kv[0])):
            results.append({
                'entity': spec.key, 'server_id': None, 'parent_id': None,
                'key': date.isoformat() if date else None,
                'modified': max(r.modified for r in rows).isoformat(),
                'deleted': False,
                'data': serialization.serialize_alp_teacher_attendance(date, rows),
            })
        return results


class PushView(MobileAPIView):
    """Batch upload with verification and a per-item report."""

    def post(self, request):
        try:
            items = validate_batch_payload(request.data)
        except ValidationError as ex:
            return Response({'detail': '; '.join(ex.messages)}, status=status.HTTP_400_BAD_REQUEST)
        device = _device(request.user, request.data)
        engine = PushEngine(request.user, device)
        batch = engine.process(str(request.data['batch_uuid'])[:64], items,
                               app_version=str(request.data.get('app_version') or '')[:64])
        return Response(batch_report(batch))


class PushHistoryView(MobileAPIView):
    def get(self, request):
        batches = MobileSyncBatch.objects.filter(user=request.user).order_by('-created')[:50]
        return Response({'batches': [
            {'batch_id': b.pk, 'batch_uuid': b.uuid, 'status': b.status,
             'received_at': b.created.isoformat(), 'summary': b.summary, 'item_count': b.item_count,
             'app_version': b.app_version}
            for b in batches
        ]})


class PushBatchView(MobileAPIView):
    def get(self, request, batch_id):
        batch = MobileSyncBatch.objects.filter(user=request.user, pk=batch_id).first()
        if batch is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(batch_report(batch))


class DuplicateCheckView(MobileAPIView):
    """Online pre-check used by the app while it has connectivity (optional)."""

    def post(self, request):
        from . import dedup
        entity = request.data.get('entity') or 'mscc.registration'
        spec = get_registry().get(entity)
        if spec is None or not spec.identity:
            return Response({'detail': 'entity must be an identity entity.'},
                            status=status.HTTP_400_BAD_REQUEST)
        identity = dedup.identity_from_payload(spec, request.data.get('data') or {})
        if not identity.complete:
            return Response({'result': [], 'complete': False})
        exclude = request.data.get('exclude_child_id')
        return Response({'result': dedup.find_duplicates(spec, identity, exclude_person_id=exclude),
                         'complete': True})
