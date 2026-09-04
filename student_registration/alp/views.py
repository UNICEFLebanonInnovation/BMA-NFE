from datetime import date, timedelta

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.conf import settings

from django.db.models import Count, Q
from django.utils import timezone
import json
from collections import Counter, OrderedDict

from .models import (
    ALPAttendanceChild, ALPRegistration, ALPTeacher, ALPGrading,
    ALPGradingDefinition,
)
from .forms import ALPRegistrationForm, ALPTeacherForm, ALPSchoolProfileForm
from .serializers import ALPRegistrationSerializer
from student_registration.students.models import Nationality
from student_registration.students.utils import generate_one_unique_id
from .tables import ALPRegistrationTable, ALPTeacherTable
from .filters import ALPRegistrationFilter, ALPTeacherFilter
from .utils import user_has_alp_permission, filter_by_school
from .export import ALPExportMixin


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
    Only school users (non-superadmins with ALP_SCHOOL group) can manage data.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            raise PermissionDenied("Superusers have read-only access to ALP data.")
        return super().dispatch(request, *args, **kwargs)

class RegistrationListView(LoginRequiredMixin, ALPUserRequiredMixin, ALPExportMixin, SingleTableMixin, FilterView):
    model = ALPRegistration
    table_class = ALPRegistrationTable
    filterset_class = ALPRegistrationFilter
    template_name = 'alp/registration_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class RegistrationAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, FormView):
    form_class = ALPRegistrationForm
    template_name = 'alp/registration_form.html'

    def get_success_url(self):
        return reverse_lazy('alp:child_profile', kwargs={'pk': self.request.session['instance_id']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.save(request=self.request)
        return super().form_valid(form)


class RegistrationEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, FormView):
    form_class = ALPRegistrationForm
    template_name = 'alp/registration_form.html'

    def get_registration(self):
        return filter_by_school(ALPRegistration.objects.all(), self.request.user).get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('alp:child_profile', kwargs={'pk': self.request.session['instance_id']})

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
        form.save(request=self.request, instance=self.get_registration())
        return super().form_valid(form)

class RegistrationDeleteView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, DeleteView):
    model = ALPRegistration
    template_name = 'alp/registration_confirm_delete.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

def child_duplication_check(request):
    """Find an existing ALP child using the same identity key as MSCC."""
    try:
        body = json.loads(request.body.decode('utf-8'))
        nationality = Nationality.objects.get(pk=body.get('nationality')).name_en
    except (ValueError, TypeError, Nationality.DoesNotExist):
        return JsonResponse({'result': []})
    unicef_id = generate_one_unique_id(
        '0', body.get('first_name'), body.get('father_name'),
        body.get('last_name'), body.get('mother_fullname'),
        '{0}-{1}-{2}'.format(body.get('birthday_year'), body.get('birthday_month'), body.get('birthday_day')),
        nationality, body.get('sex'),
    )
    matches = ALPRegistration.objects.filter(child__unicef_id=unicef_id, deleted=False)
    if body.get('registration_id'):
        try:
            current = ALPRegistration.objects.get(pk=body['registration_id'])
            matches = matches.exclude(child_id=current.child_id)
        except ALPRegistration.DoesNotExist:
            matches = matches.exclude(pk=body['registration_id'])
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
        if request.method == 'POST' and request.user.is_superuser:
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
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

from django.views.generic import CreateView, UpdateView
from .forms import ALPGradingDynamicForm

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

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, Sum


def _alp_pivot_queryset(user):
    """Return registrations in the reporting scope of ``user``."""
    queryset = ALPRegistration.objects.filter(deleted=False)
    if _is_dashboard_admin(user):
        return queryset
    return filter_by_school(queryset, user)


def _is_dashboard_admin(user):
    """Return whether ``user`` may report across every school."""
    return bool(
        getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
    )


def _dashboard_school_queryset(queryset, user):
    """Apply the connected user's school boundary to dashboard records."""
    if _is_dashboard_admin(user):
        return queryset
    return filter_by_school(queryset, user)


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
        from student_registration.schools.models import School, PartnerOrganization
        from .models import ALPRound, ALPProgram, ALPRegistration

        user = self.request.user
        instances = _dashboard_school_queryset(
            ALPRegistration.objects.filter(deleted=False), user
        )

        schools = School.objects.all()
        rounds = ALPRound.objects.all()
        programmes = ALPProgram.objects.all()

        if not _is_dashboard_admin(user):
            schools = schools.filter(id=user.school_id)

        # The template has always had a Partners KPI and a partner filter, but
        # nothing ever put `partners` in the context, so the count rendered blank
        # and the dropdown was empty. Scope it to the schools in view.
        partners = PartnerOrganization.objects.filter(
            schools__in=schools
        ).distinct().order_by('name')

        # Same for the Governorates dropdown, which rendered with no options.
        from student_registration.locations.models import Location
        governorates = Location.objects.filter(
            id__in=schools.exclude(governorate__isnull=True).values('governorate_id')
        ).order_by('name')

        return {
            'total': instances.count(),
            'schools': schools,
            'rounds': rounds,
            'programmes': programmes,
            'partners': partners,
            'governorates': governorates,
        }

class ALPDashboardDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    def get(self, request):
        from .models import ALPRegistration
        user = request.user

        qs = _dashboard_school_queryset(
            ALPRegistration.objects.filter(deleted=False), user
        )

        schools = request.GET.getlist('schools')
        if schools:
            qs = qs.filter(school_id__in=schools)

        rounds = request.GET.getlist('rounds')
        if rounds:
            qs = qs.filter(round_id__in=rounds)

        programmes = request.GET.getlist('programmes')
        if programmes:
            qs = qs.filter(programme_id__in=programmes)

        # The dashboard's partner dropdown had no counterpart here, so choosing a
        # partner changed nothing.
        partners = request.GET.getlist('partners')
        if partners:
            qs = qs.filter(school__partner_schools__id__in=partners).distinct()

        governorates = request.GET.getlist('governorates')
        if governorates:
            qs = qs.filter(school__governorate_id__in=governorates)

        def aggregate(queryset, field):
            results = queryset.values(field).annotate(total=Count('id')).order_by(field)
            data = []
            for row in results:
                name = row.get(field) or 'N/A'
                data.append({'name': name, 'y': row['total']})
            return data

        # The chart containers on dashboard_registration.html and the script that
        # fills them (alp/alp_dashboard_d3.js) both expect the `children_*` keys
        # below. This endpoint used to answer with `nationality`/`gender`/`round`
        # /`programme` instead, so every chart on the page drew nothing even once
        # the script was loading from the right path.
        current_year = date.today().year

        gender_age_counts = {}
        for row in qs.values('child__gender', 'child__birthday_year').annotate(total=Count('id')):
            gender = row['child__gender'] or 'Unknown'
            try:
                age = current_year - int(row['child__birthday_year'])
                if age < 5:
                    age_group = '< 5'
                elif age < 10:
                    age_group = '5-9'
                elif age < 15:
                    age_group = '10-14'
                elif age < 18:
                    age_group = '15-17'
                else:
                    age_group = '18+'
            except (ValueError, TypeError):
                age_group = 'Unknown'
            label = '{} - {}'.format(gender, age_group)
            gender_age_counts[label] = gender_age_counts.get(label, 0) + row['total']

        programme_counts = Counter()
        for programmes_value in qs.values_list('cash_support_programmes', flat=True):
            if programmes_value:
                programme_counts.update(programmes_value)
        cash_support = [
            {'name': label, 'y': programme_counts.get(value, 0)}
            for value, label in ALPRegistration.CASH_SUPPORT_PROGRAMMES
            if value
        ]

        per_round = (
            qs.values('round__name')
            .annotate(total=Count('child', distinct=True))
            .order_by('round__name')
        )
        round_names = [row.get('round__name') or 'N/A' for row in per_round]
        per_round_dict = {name: row['total'] for name, row in zip(round_names, per_round)}

        multi_round_children = list(
            qs.values('child')
            .annotate(round_count=Count('round', distinct=True))
            .filter(round_count__gt=1)
            .values_list('child', flat=True)
        )
        moved_per_round = (
            qs.filter(child__in=multi_round_children)
            .values('round__name')
            .annotate(total=Count('child', distinct=True))
            .order_by('round__name')
        )
        moved_dict = {row.get('round__name') or 'N/A': row['total'] for row in moved_per_round}

        gradings = ALPGrading.objects.filter(
            registration_id__in=qs.values('id')
        ).only('registration_id', 'grading_data', 'created').order_by('created')
        learning_outcomes = build_learning_outcome_data(
            gradings, ALPGradingDefinition.objects.all()
        )

        response_data = {
            'children_per_gender': aggregate(qs, 'child__gender'),
            'children_per_status': aggregate(qs, 'child__marital_status'),
            'children_per_nationality': aggregate(qs, 'child__nationality__name'),
            'children_per_disability': aggregate(qs, 'child__disability__name'),
            'children_per_source': aggregate(qs, 'source_of_identification'),
            'children_gender_age': [
                {'name': name, 'y': count} for name, count in sorted(gender_age_counts.items())
            ],
            'children_cash_support': cash_support,
            'children_per_round': [
                {'name': name, 'y': per_round_dict[name]} for name in round_names
            ],
            'children_moved_rounds': {
                'categories': round_names,
                'moved': [moved_dict.get(name, 0) for name in round_names],
                'new': [per_round_dict[name] - moved_dict.get(name, 0) for name in round_names],
            },
            'learning_outcomes': learning_outcomes,
        }

        return JsonResponse(response_data)

class ALPTeacherDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_teacher.html'

    def get_context_data(self, **kwargs):
        from student_registration.schools.models import School
        from .models import (
            ALPProgram,
            ALPRegistration,
            ALPRound,
            ALPTeacher,
            ALPTeacherAttendance,
        )

        user = self.request.user
        instances = _dashboard_school_queryset(ALPTeacher.objects.all(), user)

        schools = School.objects.all()
        rounds = ALPRound.objects.all()

        if not _is_dashboard_admin(user):
            schools = schools.filter(id=user.school_id)

        programmes = ALPProgram.objects.all()
        selected_school = self.request.GET.get('school', '')
        selected_programme = self.request.GET.get('programme', '')
        today = _current_date()
        default_start = today - timedelta(days=180)

        try:
            start_date = timezone.datetime.strptime(
                self.request.GET.get('start_date', ''), '%Y-%m-%d'
            ).date()
        except (TypeError, ValueError):
            start_date = default_start
        try:
            end_date = timezone.datetime.strptime(
                self.request.GET.get('end_date', ''), '%Y-%m-%d'
            ).date()
        except (TypeError, ValueError):
            end_date = today

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        if selected_school:
            instances = instances.filter(school_id=selected_school)
        if selected_programme:
            programme_school_ids = ALPRegistration.objects.filter(
                programme_id=selected_programme
            ).values_list('school_id', flat=True)
            instances = instances.filter(school_id__in=programme_school_ids)

        attendance = ALPTeacherAttendance.objects.filter(
            teacher__in=instances,
            date__range=(start_date, end_date),
        ).select_related('teacher__school')

        records = list(attendance.values(
            'date', 'status', 'teacher_id', 'teacher__school_id', 'teacher__school__name'
        ))
        present = sum(row['status'] == 'Present' for row in records)
        rate = round((present / len(records)) * 100, 1) if records else 0

        monthly = {}
        school_totals = {}
        for row in records:
            month = row['date'].strftime('%Y-%m') if row['date'] else 'Unknown'
            monthly.setdefault(month, {'present': 0, 'total': 0})
            monthly[month]['total'] += 1
            monthly[month]['present'] += row['status'] == 'Present'

            school_name = row['teacher__school__name'] or 'Unassigned'
            school_totals.setdefault(school_name, {'present': 0, 'total': 0})
            school_totals[school_name]['total'] += 1
            school_totals[school_name]['present'] += row['status'] == 'Present'

        trend = [
            {'month': month, 'rate': round(values['present'] / values['total'] * 100, 1)}
            for month, values in sorted(monthly.items())
        ]
        by_school = [
            {'school': name, 'rate': round(values['present'] / values['total'] * 100, 1),
             'records': values['total']}
            for name, values in sorted(school_totals.items(), key=lambda item: item[1]['total'], reverse=True)
        ]

        programme_rows = []
        for programme in programmes:
            programme_school_ids = set(ALPRegistration.objects.filter(
                programme=programme
            ).values_list('school_id', flat=True))
            relevant = [row for row in records if row['teacher__school_id'] in programme_school_ids]
            programme_present = sum(row['status'] == 'Present' for row in relevant)
            programme_rows.append({
                'programme': programme.name,
                'rate': round(programme_present / len(relevant) * 100, 1) if relevant else 0,
                'records': len(relevant),
            })

        return {
            'total': instances.count(),
            'schools': schools,
            'rounds': rounds,
        }


class ALPTeacherDashboardDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    """Return teacher workforce indicators within the user's ALP school scope."""

    def get(self, request):
        teachers = _dashboard_school_queryset(ALPTeacher.objects.all(), request.user)

        school_ids = request.GET.getlist('schools')
        if school_ids:
            teachers = teachers.filter(school_id__in=school_ids)

        round_ids = request.GET.getlist('rounds')
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

class ALPAttendanceDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        year = int(self.request.GET.get('year', timezone.now().year))
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


def _alp_attendance_queryset(user):
    """Return child attendance records visible to an ALP user."""
    queryset = ALPAttendanceChild.objects.all()
    if not _is_dashboard_admin(user):
        queryset = queryset.filter(attendance_day__school_id=user.school_id)
    return queryset


def _aggregate_alp_attendance(queryset, *group_fields):
    """Aggregate total and absent child records for heatmap groups."""
    return (
        queryset.values(*group_fields)
        .annotate(total=Count('id'), absent=Count('id', filter=Q(attended='No')))
        .order_by(*group_fields)
    )

class ALPSchoolDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_school.html'

    def get_context_data(self, **kwargs):
        from student_registration.schools.models import School

        user = self.request.user

        schools = School.objects.all()

        if not _is_dashboard_admin(user):
            schools = schools.filter(id=user.school_id)

        return {
            'total': schools.count(),
            'schools': schools,
        }

      
class ALPSchoolGeoDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    """Return map-ready school data within the current ALP user's scope."""

    def get(self, request):
        from django.db.models import Count
        from student_registration.schools.models import School

        schools = School.objects.select_related(
            'governorate', 'district', 'cadaster'
        ).filter(
            latitude__isnull=False, longitude__isnull=False
        ).order_by('name')

        if not _is_dashboard_admin(request.user):
            if not request.user.school_id:
                return JsonResponse([], safe=False)
            schools = schools.filter(id=request.user.school_id)

        school_id = request.GET.get('school_id')
        if school_id:
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
      
      
import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models.functions import TruncDate
from student_registration.backends.models import ExportHistory

class ALPLandingPage(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = _current_date()
        week_start = today - timezone.timedelta(days=6)
        trend_start = today - timezone.timedelta(days=13)
        month_start = today.replace(day=1)

        user = self.request.user

        # apply school filtering for standard users
        registrations = ALPRegistration.objects.filter(deleted=False)
        if not _is_dashboard_admin(user):
            registrations = registrations.filter(school_id=user.school_id)

        today_count = registrations.filter(created__date=today).count()
        week_count = registrations.filter(created__date__gte=week_start).count()
        schools_reporting = registrations.filter(
            created__date__gte=today - timezone.timedelta(days=30),
            school__isnull=False,
        ).values('school_id').distinct().count()

        attendance_rows = ALPAttendanceChild.objects.filter(
            attendance_day__attendance_date__gte=month_start,
            attendance_day__attendance_date__lte=today,
        )
        if not _is_dashboard_admin(user):
            attendance_rows = attendance_rows.filter(attendance_day__school_id=user.school_id)

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
            day = trend_start + timezone.timedelta(days=idx)
            key = day.strftime('%Y-%m-%d')
            trend_data.append({'date': key, 'value': trend_map.get(key, 0)})

        recent_exports = ExportHistory.objects.filter(
            export_type__icontains='ALP'
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
                'file_url': export.file.url if export.file and export.file.name else '#',
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
