import json
from collections import Counter, OrderedDict
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView, DeleteView, DetailView, FormView, TemplateView, UpdateView, View,
)
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from student_registration.backends.models import ExportHistory
from student_registration.schools.models import School
from student_registration.students.models import Nationality
from student_registration.students.utils import generate_one_unique_id

from .export import ALPExportMixin
from .filters import ALPRegistrationFilter, ALPTeacherFilter
from .forms import ALPGradingDynamicForm, ALPRegistrationForm, ALPSchoolProfileForm, ALPTeacherForm
from .models import (
    ALPAttendanceChild, ALPGrading, ALPGradingDefinition, ALPProgram,
    ALPRegistration, ALPRound, ALPTeacher,
)
from .serializers import ALPRegistrationSerializer
from .tables import ALPRegistrationTable, ALPTeacherTable
from .utils import filter_by_school, parse_int, parse_int_list, user_has_alp_permission

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


def _current_date():
    """Return today's date without localizing a naive datetime."""
    if settings.USE_TZ:
        return timezone.localdate()
    return timezone.now().date()


def _normalise_grade(value, definition):
    """Return a grade as a percentage of its configured grading range."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    grade_range = definition.max_grade - definition.min_grade
    if grade_range <= 0:
        return None
    percentage = ((value - definition.min_grade) / grade_range) * 100
    return max(0, min(100, percentage))


def build_learning_outcome_data(gradings, definitions):
    """Summarise latest outcomes and change since each child's first assessment."""
    definitions = {str(item.id): item for item in definitions}
    assessments = {}
    subject_totals = {key: [] for key in definitions}

    for grading in gradings:
        scores = []
        for definition_id, value in (grading.grading_data or {}).items():
            definition = definitions.get(str(definition_id))
            if not definition:
                continue
            percentage = _normalise_grade(value, definition)
            if percentage is not None:
                scores.append(percentage)

        if scores and grading.registration_id:
            assessments.setdefault(grading.registration_id, []).append(
                (grading.created, sum(scores) / len(scores), grading.grading_data)
            )

    latest_scores = []
    progress = {'Improved': 0, 'Stable': 0, 'Declined': 0}
    for registration_assessments in assessments.values():
        registration_assessments.sort(key=lambda item: item[0])
        latest = registration_assessments[-1]
        latest_scores.append(latest[1])

        for definition_id, value in (latest[2] or {}).items():
            definition = definitions.get(str(definition_id))
            if definition:
                percentage = _normalise_grade(value, definition)
                if percentage is not None:
                    subject_totals[str(definition_id)].append(percentage)

        if len(registration_assessments) > 1:
            change = latest[1] - registration_assessments[0][1]
            if change > 0.5:
                progress['Improved'] += 1
            elif change < -0.5:
                progress['Declined'] += 1
            else:
                progress['Stable'] += 1

    bands = {'On track': 0, 'Developing': 0, 'Needs support': 0}
    for score in latest_scores:
        if score >= 75:
            bands['On track'] += 1
        elif score >= 50:
            bands['Developing'] += 1
        else:
            bands['Needs support'] += 1

    subjects = []
    for definition_id, scores in subject_totals.items():
        if scores:
            subjects.append({
                'name': definitions[definition_id].material,
                'y': round(sum(scores) / len(scores), 1),
            })
    subjects.sort(key=lambda item: item['name'])

    return {
        'assessed_children': len(latest_scores),
        'average_achievement': (
            round(sum(latest_scores) / len(latest_scores), 1)
            if latest_scores else None
        ),
        'children_with_follow_up': sum(progress.values()),
        'improved_children': progress['Improved'],
        'performance_bands': [
            {'name': name, 'y': total} for name, total in bands.items()
        ],
        'progress': [
            {'name': name, 'y': total} for name, total in progress.items()
        ],
        'subjects': subjects,
    }


class ALPUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_has_alp_permission(self.request.user)


class ALPPivotUserRequiredMixin(UserPassesTestMixin):
    """Allow ALP focal points and site administrators into ALP reporting."""

    def test_func(self):
        user = self.request.user
        return user.is_staff or user_has_alp_permission(user)


class ALPEditPermissionMixin(object):
    """
    Superadmins can see all schools info in read-only mode.
    Only school users (non-superadmins with ALP_SCHOOL group) that are
    connected to a school can manage data.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            raise PermissionDenied("Superusers have read-only access to ALP data.")
        if getattr(request.user, 'school_id', None) is None:
            raise PermissionDenied("Your account is not assigned to a school.")
        return super().dispatch(request, *args, **kwargs)


def _active_registrations(user):
    """Registrations of the user's school that have not been soft deleted."""
    return filter_by_school(ALPRegistration.objects.filter(deleted=False), user)


class RegistrationListView(LoginRequiredMixin, ALPUserRequiredMixin, ALPExportMixin, SingleTableMixin, FilterView):
    model = ALPRegistration
    table_class = ALPRegistrationTable
    filterset_class = ALPRegistrationFilter
    template_name = 'alp/registration_list.html'

    def get_queryset(self):
        qs = super().get_queryset().filter(deleted=False)
        return filter_by_school(qs, self.request.user)


class RegistrationAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, FormView):
    form_class = ALPRegistrationForm
    template_name = 'alp/registration_form.html'
    registration = None

    def get_success_url(self):
        return reverse('alp:child_profile', kwargs={'pk': self.registration.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.registration = form.save(request=self.request)
        if self.registration is None:
            # The serializer rejected the submission: show the errors instead
            # of redirecting to a profile that was never created.
            return self.form_invalid(form)
        return super().form_valid(form)


class RegistrationEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, FormView):
    form_class = ALPRegistrationForm
    template_name = 'alp/registration_form.html'
    registration = None

    def get_registration(self):
        if not hasattr(self, '_registration'):
            registration = get_object_or_404(
                _active_registrations(self.request.user).select_related('child'),
                pk=self.kwargs['pk'],
            )
            if registration.child is None:
                raise Http404("This registration has no child record.")
            self._registration = registration
        return self._registration

    def get_success_url(self):
        return reverse('alp:child_profile', kwargs={'pk': self.registration.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = self.get_registration()
        kwargs.update(instance=instance, request=self.request)
        if self.request.method == 'GET':
            data = ALPRegistrationSerializer(instance).data
            for field in ('child_nationality', 'child_disability', 'main_caregiver_nationality',
                          'father_educational_level', 'mother_educational_level', 'id_type'):
                data[field] = data.get(field + '_id', '')
            kwargs['initial'] = data
        return kwargs

    def form_valid(self, form):
        self.registration = form.save(request=self.request, instance=self.get_registration())
        if self.registration is None:
            return self.form_invalid(form)
        return super().form_valid(form)


class RegistrationDeleteView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, DeleteView):
    model = ALPRegistration
    template_name = 'alp/registration_confirm_delete.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_queryset(self):
        return _active_registrations(self.request.user)

    def form_valid(self, form):
        """
        Soft delete the registration.

        Every ALP report already excludes ``deleted`` rows; a hard delete would
        orphan the child's attendance and grading history instead.
        """
        self.object.deleted = True
        self.object.deleted_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        messages.success(self.request, _('The registration has been deleted.'))
        return HttpResponseRedirect(self.get_success_url())


@login_required
@require_POST
def child_duplication_check(request):
    """Find an existing ALP child using the same identity key as MSCC."""
    if not user_has_alp_permission(request.user):
        raise PermissionDenied
    try:
        body = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({'result': []})
    if not isinstance(body, dict):
        return JsonResponse({'result': []})
    nationality = Nationality.objects.filter(pk=parse_int(body.get('nationality'))).first()
    if nationality is None:
        return JsonResponse({'result': []})
    unicef_id = generate_one_unique_id(
        '0', body.get('first_name'), body.get('father_name'),
        body.get('last_name'), body.get('mother_fullname'),
        '{0}-{1}-{2}'.format(body.get('birthday_year'), body.get('birthday_month'), body.get('birthday_day')),
        nationality.name_en, body.get('sex'),
    )
    if not unicef_id:
        # The unique-id service is unavailable: do not flag every child as a duplicate.
        return JsonResponse({'result': []})
    matches = ALPRegistration.objects.filter(child__unicef_id=unicef_id, deleted=False)
    registration_id = parse_int(body.get('registration_id'))
    if registration_id:
        current = ALPRegistration.objects.filter(pk=registration_id).first()
        if current is not None and current.child_id:
            matches = matches.exclude(child_id=current.child_id)
        else:
            matches = matches.exclude(pk=registration_id)
    result = matches.values(
        'id', 'school__name', 'child__first_name', 'child__father_name',
        'child__last_name', 'child__mother_fullname', 'child__birthday_day',
        'child__birthday_month', 'child__birthday_year',
    )[:10]
    return JsonResponse({'result': list(result)})


class TeacherListView(LoginRequiredMixin, ALPUserRequiredMixin, ALPExportMixin, SingleTableMixin, FilterView):
    model = ALPTeacher
    table_class = ALPTeacherTable
    filterset_class = ALPTeacherFilter
    template_name = 'alp/teacher_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)


class TeacherAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPTeacher
    form_class = ALPTeacherForm
    template_name = 'alp/teacher_form.html'
    success_url = reverse_lazy('alp:teacher_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.modified_by = self.request.user
        form.instance.school = self.request.user.school
        return super().form_valid(form)


class TeacherEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPTeacher
    form_class = ALPTeacherForm
    template_name = 'alp/teacher_form.html'
    success_url = reverse_lazy('alp:teacher_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        form.instance.school = self.request.user.school
        return super().form_valid(form)


class TeacherDeleteView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, DeleteView):
    model = ALPTeacher
    template_name = 'alp/teacher_confirm_delete.html'
    success_url = reverse_lazy('alp:teacher_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)


class SchoolProfileView(LoginRequiredMixin, ALPUserRequiredMixin, UpdateView):
    """Display a school profile and let its focal point update it."""

    form_class = ALPSchoolProfileForm
    template_name = 'alp/school_profile.html'
    success_url = reverse_lazy('alp:school_profile')

    def get_object(self, queryset=None):
        school = self.request.user.school
        if school is None:
            raise PermissionDenied("Your account is not assigned to a school.")
        return school

    def dispatch(self, request, *args, **kwargs):
        if request.method not in SAFE_METHODS and request.user.is_superuser:
            raise PermissionDenied("Superusers have read-only access to ALP data.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        messages.success(self.request, 'School information updated successfully.')
        return super().form_valid(form)


class ChildProfileView(LoginRequiredMixin, ALPUserRequiredMixin, DetailView):
    model = ALPRegistration
    template_name = 'alp/child_profile.html'
    context_object_name = 'registration'

    def get_queryset(self):
        return _active_registrations(self.request.user).select_related('child', 'school', 'round', 'programme')


class GradingAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPGrading
    form_class = ALPGradingDynamicForm
    template_name = 'alp/grading_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class GradingEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPGrading
    form_class = ALPGradingDynamicForm
    template_name = 'alp/grading_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)


def _is_dashboard_admin(user):
    """Return whether ``user`` may report across every school."""
    return bool(
        getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
    )


def _alp_pivot_queryset(user):
    """Return registrations in the reporting scope of ``user``."""
    queryset = ALPRegistration.objects.filter(deleted=False)
    if _is_dashboard_admin(user):
        return queryset
    return filter_by_school(queryset, user)


def _dashboard_school_queryset(queryset, user):
    """Apply the connected user's school boundary to dashboard records."""
    if _is_dashboard_admin(user):
        return queryset
    return filter_by_school(queryset, user)


def _dashboard_schools(user):
    """Schools offered as dashboard filters for ``user``."""
    schools = School.objects.all()
    if not _is_dashboard_admin(user):
        schools = schools.filter(id=user.school_id)
    return schools


class ALPPivotDashboardView(
        LoginRequiredMixin, ALPPivotUserRequiredMixin, TemplateView):
    """Display the interactive pivot builder using ALP registrations only."""

    template_name = 'alp/pivot_dashboard.html'


class ALPPivotDataView(LoginRequiredMixin, ALPPivotUserRequiredMixin, View):
    """Return ALP registration dimensions within the connected user's scope."""

    def get(self, request):
        queryset = _alp_pivot_queryset(request.user).values(
            'school__number',
            'school__name',
            'school__governorate__name',
            'school__district__name',
            'school__cadaster__name',
            'child__gender',
            'child__nationality__name',
            'child__birthday_year',
            'round__name',
            'programme__name',
            'registration_date',
            'have_labour',
            'labour_type',
            'labour_weekly_income',
            'source_of_identification',
            'type',
        )

        data = []
        for registration in queryset.iterator():
            registration_date = registration['registration_date']
            data.append({
                'school_number': registration['school__number'] or '',
                'school': registration['school__name'] or '',
                'governorate': registration['school__governorate__name'] or '',
                'district': registration['school__district__name'] or '',
                'cadaster': registration['school__cadaster__name'] or '',
                'gender': registration['child__gender'] or '',
                'nationality': registration['child__nationality__name'] or '',
                'birth_year': registration['child__birthday_year'] or '',
                'round': registration['round__name'] or '',
                'programme': registration['programme__name'] or '',
                'registration_date': (
                    registration_date.isoformat() if registration_date else ''
                ),
                'participates_in_work': registration['have_labour'] or '',
                'work_type': registration['labour_type'] or '',
                'weekly_income': registration['labour_weekly_income'] or '',
                'referral_source': registration['source_of_identification'] or '',
                'registration_type': registration['type'] or '',
            })

        return JsonResponse(data, safe=False)


class ALPRegistrationDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_registration.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        instances = _dashboard_school_queryset(
            ALPRegistration.objects.filter(deleted=False), user
        )

        return {
            'total': instances.count(),
            'schools': _dashboard_schools(user),
            'rounds': ALPRound.objects.all(),
            'programmes': ALPProgram.objects.all(),
        }


def _aggregate_registrations(queryset, field):
    results = queryset.values(field).annotate(total=Count('id')).order_by(field)
    return [{'name': row.get(field) or 'N/A', 'y': row['total']} for row in results]


def _age_group(birth_year, current_year):
    try:
        age = current_year - int(birth_year)
    except (TypeError, ValueError):
        return 'Unknown'
    if age < 5:
        return '< 5'
    if age < 10:
        return '5-9'
    if age < 15:
        return '10-14'
    if age < 18:
        return '15-17'
    return '18+'


class ALPDashboardDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    """Return the datasets rendered by the ALP registration dashboard charts."""

    def get(self, request):
        user = request.user

        qs = _dashboard_school_queryset(
            ALPRegistration.objects.filter(deleted=False), user
        )

        schools = parse_int_list(request.GET.getlist('schools'))
        if schools:
            qs = qs.filter(school_id__in=schools)

        rounds = parse_int_list(request.GET.getlist('rounds'))
        if rounds:
            qs = qs.filter(round_id__in=rounds)

        programmes = parse_int_list(request.GET.getlist('programmes'))
        if programmes:
            qs = qs.filter(programme_id__in=programmes)

        nationality_data = _aggregate_registrations(qs, 'child__nationality__name_en')
        gender_data = _aggregate_registrations(qs, 'child__gender')
        round_data = _aggregate_registrations(qs, 'round__name')
        programme_data = _aggregate_registrations(qs, 'programme__name')

        current_year = _current_date().year
        gender_age_counts = OrderedDict()
        gender_age_rows = qs.values('child__gender', 'child__birthday_year').annotate(
            total=Count('id')
        ).order_by('child__gender', 'child__birthday_year')
        for row in gender_age_rows:
            label = '{0} - {1}'.format(
                row['child__gender'] or 'Unknown',
                _age_group(row['child__birthday_year'], current_year),
            )
            gender_age_counts[label] = gender_age_counts.get(label, 0) + row['total']

        cash_counts = Counter()
        for cash_programmes in qs.values_list('cash_support_programmes', flat=True):
            if cash_programmes:
                cash_counts.update(cash_programmes)
        cash_support = [
            {'name': value, 'y': cash_counts.get(value, 0)}
            for value, _label in ALPRegistration.CASH_SUPPORT_PROGRAMMES if value
        ]

        per_round = qs.values('round__name').annotate(
            total=Count('child', distinct=True)
        ).order_by('round__name')
        round_names = [row.get('round__name') or 'N/A' for row in per_round]
        per_round_totals = {name: row['total'] for name, row in zip(round_names, per_round)}
        multi_round_children = list(
            qs.values('child')
            .annotate(round_count=Count('round', distinct=True))
            .filter(round_count__gt=1)
            .values_list('child', flat=True)
        )
        moved_per_round = {}
        if multi_round_children:
            moved_rows = qs.filter(child__in=multi_round_children).values('round__name').annotate(
                total=Count('child', distinct=True)
            ).order_by('round__name')
            moved_per_round = {row.get('round__name') or 'N/A': row['total'] for row in moved_rows}

        gradings = ALPGrading.objects.filter(
            registration_id__in=qs.values('id')
        ).only('registration_id', 'grading_data', 'created').order_by('created')
        learning_outcomes = build_learning_outcome_data(
            gradings, ALPGradingDefinition.objects.all()
        )

        response_data = {
            'nationality': nationality_data,
            'gender': gender_data,
            'round': round_data,
            'programme': programme_data,
            'learning_outcomes': learning_outcomes,
            # Datasets consumed by static/js/alp/alp_dashboard_d3.js
            'children_per_gender': gender_data,
            'children_gender_age': [{'name': name, 'y': total} for name, total in gender_age_counts.items()],
            'children_per_nationality': nationality_data,
            'children_per_source': _aggregate_registrations(qs, 'source_of_identification'),
            'children_per_status': _aggregate_registrations(qs, 'child__living_arrangement'),
            'children_per_disability': _aggregate_registrations(qs, 'child__disability__name'),
            'children_cash_support': cash_support,
            'children_per_round': [{'name': name, 'y': per_round_totals[name]} for name in round_names],
            'children_per_programme': programme_data,
            'children_moved_rounds': {
                'categories': round_names,
                'moved': [moved_per_round.get(name, 0) for name in round_names],
                'new': [per_round_totals[name] - moved_per_round.get(name, 0) for name in round_names],
            },
        }

        return JsonResponse(response_data)


class ALPTeacherDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_teacher.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        instances = _dashboard_school_queryset(ALPTeacher.objects.all(), user)

        return {
            'total': instances.count(),
            'schools': _dashboard_schools(user),
            'rounds': ALPRound.objects.all(),
        }


class ALPTeacherDashboardDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    """Return teacher workforce indicators within the user's ALP school scope."""

    def get(self, request):
        teachers = _dashboard_school_queryset(ALPTeacher.objects.all(), request.user)

        school_ids = parse_int_list(request.GET.getlist('schools'))
        if school_ids:
            teachers = teachers.filter(school_id__in=school_ids)

        round_ids = parse_int_list(request.GET.getlist('rounds'))
        if round_ids:
            teachers = teachers.filter(round_id__in=round_ids)

        total = teachers.count()
        trained = teachers.filter(
            Q(trainings__isnull=False) | Q(training_sessions_attended__gt=0)
        ).distinct().count()
        contactable = teachers.exclude(
            Q(phone_number__isnull=True) | Q(phone_number='')
        ).count()
        averages = teachers.aggregate(
            experience=Avg('years_of_experience'),
            sessions=Avg('training_sessions_attended'),
        )
        hours = teachers.aggregate(
            alp=Sum('teaching_hours_mscc'),
            private=Sum('teaching_hours_private_school'),
        )

        def percent(value):
            return round(value * 100 / total, 1) if total else 0

        def grouped(field):
            rows = teachers.values(field).annotate(y=Count('id')).order_by(field)
            return [
                {'name': row[field] or 'Not specified', 'y': row['y']}
                for row in rows
            ]

        subjects = {}
        levels = {}
        for teacher in teachers.only('subjects_provided', 'registration_level'):
            for subject in teacher.subjects_provided or []:
                if subject:
                    subjects[subject] = subjects.get(subject, 0) + 1
            for level in teacher.registration_level or []:
                if level:
                    levels[level] = levels.get(level, 0) + 1

        training_rows = (
            teachers.filter(trainings__isnull=False)
            .values('trainings__name')
            .annotate(y=Count('id', distinct=True))
            .order_by('-y', 'trainings__name')
        )

        return JsonResponse({
            'total': total,
            'schools': teachers.exclude(school_id__isnull=True).values('school_id').distinct().count(),
            'trained': trained,
            'trained_percent': percent(trained),
            'contact_percent': percent(contactable),
            'average_experience': round(averages['experience'] or 0, 1),
            'average_sessions': round(averages['sessions'] or 0, 1),
            'gender': grouped('sex'),
            'nationality': grouped('nationality__name'),
            'school': grouped('school__name'),
            'round': grouped('round__name'),
            'assignment': grouped('teacher_assignment'),
            'coaching': grouped('extra_coaching'),
            'subjects': [{'name': key, 'y': value} for key, value in subjects.items()],
            'levels': [{'name': key, 'y': value} for key, value in levels.items()],
            'trainings': [
                {'name': row['trainings__name'] or 'Not specified', 'y': row['y']}
                for row in training_rows
            ],
            'hours': [
                {'name': 'ALP', 'y': hours['alp'] or 0},
                {'name': 'Private school', 'y': hours['private'] or 0},
            ],
        })


def _alp_attendance_queryset(user):
    """Return child attendance records visible to an ALP user."""
    queryset = ALPAttendanceChild.objects.all()
    if _is_dashboard_admin(user):
        return queryset
    if getattr(user, 'school_id', None) is None:
        return queryset.none()
    return queryset.filter(attendance_day__school_id=user.school_id)


def _aggregate_alp_attendance(queryset, *group_fields):
    """Aggregate total and absent child records for heatmap groups."""
    return (
        queryset.values(*group_fields)
        .annotate(total=Count('id'), absent=Count('id', filter=Q(attended='No')))
        .order_by(*group_fields)
    )


class ALPAttendanceDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        year = parse_int(self.request.GET.get('year'))
        if year is None or not 1900 <= year <= 2100:
            year = _current_date().year
        base_qs = _alp_attendance_queryset(user).filter(
            attendance_day__attendance_date__year=year,
        )
        attendance = _aggregate_alp_attendance(base_qs, 'attendance_day__attendance_date')
        programme_attendance = _aggregate_alp_attendance(
            base_qs, 'attendance_day__attendance_date', 'attendance_day__programme__name'
        )

        programme_data = OrderedDict()
        for row in programme_attendance:
            programme = row.pop('attendance_day__programme__name') or 'Unknown'
            programme_data.setdefault(programme, []).append(row)

        years = _alp_attendance_queryset(user).dates('attendance_day__attendance_date', 'year')
        context.update({
            'attendance_json': json.dumps(list(attendance), default=str),
            'program_attendance_json': json.dumps(programme_data, default=str),
            'year': year,
            'years': [date.year for date in years],
        })
        return context


class ALPSchoolDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_school.html'

    def get_context_data(self, **kwargs):
        schools = _dashboard_schools(self.request.user)

        return {
            'total': schools.count(),
            'schools': schools,
        }


class ALPSchoolGeoDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    """Return map-ready school data within the current ALP user's scope."""

    def get(self, request):
        schools = School.objects.select_related(
            'governorate', 'district', 'cadaster'
        ).filter(
            latitude__isnull=False, longitude__isnull=False
        ).order_by('name')

        if not _is_dashboard_admin(request.user):
            if not request.user.school_id:
                return JsonResponse([], safe=False)
            schools = schools.filter(id=request.user.school_id)

        school_id = parse_int(request.GET.get('school_id'))
        if school_id is not None:
            schools = schools.filter(id=school_id)

        school_list = list(schools)
        school_ids = [school.id for school in school_list]
        registration_stats = {
            row['school_id']: row['total']
            for row in ALPRegistration.objects.filter(
                school_id__in=school_ids, deleted=False
            ).values('school_id').annotate(total=Count('id'))
        }
        teacher_stats = {
            row['school_id']: row['total']
            for row in ALPTeacher.objects.filter(
                school_id__in=school_ids
            ).values('school_id').annotate(total=Count('id'))
        }

        data = [{
            'id': school.id,
            'number': school.number,
            'name': school.name,
            'type': school.get_type_display() if school.type else 'N/A',
            'governorate': (
                school.governorate.name if school.governorate else 'N/A'
            ),
            'district': school.district.name if school.district else 'N/A',
            'cadaster': school.cadaster.name if school.cadaster else 'N/A',
            'latitude': school.latitude,
            'longitude': school.longitude,
            'students': registration_stats.get(school.id, 0),
            'teachers': teacher_stats.get(school.id, 0),
            'capacity': school.school_capacity or 0,
            'cwd_accessible': (
                school.get_CWD_accessible_display()
                if school.CWD_accessible else 'N/A'
            ),
            'internet_available': (
                school.get_internet_available_display()
                if school.internet_available else 'N/A'
            ),
        } for school in school_list]

        return JsonResponse(data, safe=False)


class ALPLandingPage(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = _current_date()
        week_start = today - timedelta(days=6)
        trend_start = today - timedelta(days=13)
        month_start = today.replace(day=1)

        user = self.request.user

        # apply school filtering for standard users
        registrations = _dashboard_school_queryset(
            ALPRegistration.objects.filter(deleted=False), user
        )

        today_count = registrations.filter(created__date=today).count()
        week_count = registrations.filter(created__date__gte=week_start).count()
        schools_reporting = registrations.filter(
            created__date__gte=today - timedelta(days=30),
            school__isnull=False,
        ).values('school_id').distinct().count()

        attendance_rows = _alp_attendance_queryset(user).filter(
            attendance_day__attendance_date__gte=month_start,
            attendance_day__attendance_date__lte=today,
        )

        attendance_total = attendance_rows.count()
        attendance_yes = attendance_rows.filter(attended='Yes').count()
        attendance_percent = round((attendance_yes / attendance_total) * 100) if attendance_total else 0

        trend_map = {
            row['day'].strftime('%Y-%m-%d'): row['value']
            for row in registrations.filter(created__date__gte=trend_start)
            .annotate(day=TruncDate('created'))
            .values('day')
            .annotate(value=Count('id'))
        }
        trend_data = []
        for idx in range(14):
            day = trend_start + timedelta(days=idx)
            key = day.strftime('%Y-%m-%d')
            trend_data.append({'date': key, 'value': trend_map.get(key, 0)})

        # Only the connected user's own exports: export files must not leak
        # between schools.
        recent_exports = ExportHistory.objects.filter(
            export_type__icontains='ALP', created_by=user,
        ).order_by('-created')[:5]
        export_rows = []
        for export in recent_exports:
            created = export.created
            if created and timezone.is_aware(created):
                created_display = timezone.localtime(created).strftime('%Y-%m-%d %H:%M')
            elif created:
                created_display = created.strftime('%Y-%m-%d %H:%M')
            else:
                created_display = ''
            export_rows.append({
                'export_type': export.export_type,
                'created_display': created_display,
                'status': export.status,
                'file_url': export.file_url or '#',
            })

        context.update({
            'kpi_today': today_count,
            'kpi_week': week_count,
            'kpi_schools': schools_reporting,
            'kpi_attendance': attendance_percent,
            'trend_data': json.dumps(trend_data),
            'recent_exports': export_rows,
        })
        return context
