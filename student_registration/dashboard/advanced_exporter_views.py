from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

from student_registration.mscc.models import Registration, Teacher
from student_registration.locations.models import Center
from student_registration.clm.models import PartnerOrganization
from student_registration.mscc.models import Round
from student_registration.backends.models import ExportHistory
from student_registration.mscc.tasks import _get_executor, _run_with_new_db_connection
from .advanced_exporter import _generate_advanced_export

class AdvancedExporterDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/advanced_exporter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Available fields mapping
        # These are basic fields, we can expand on related fields via __
        registration_fields = [
            {'id': 'id', 'label': 'Registration ID'},
            {'id': 'child__unicef_id', 'label': 'UNICEF ID'},
            {'id': 'child__first_name', 'label': 'First Name'},
            {'id': 'child__last_name', 'label': 'Last Name'},
            {'id': 'child__gender', 'label': 'Gender'},
            {'id': 'child__nationality__name', 'label': 'Nationality'},
            {'id': 'child__birthday_year', 'label': 'Birth Year'},
            {'id': 'center__name', 'label': 'Center Name'},
            {'id': 'partner__name', 'label': 'Partner Name'},
            {'id': 'round__name', 'label': 'Round Name'},
            {'id': 'created', 'label': 'Registration Date'},
        ]

        center_fields = [
            {'id': 'id', 'label': 'Center ID'},
            {'id': 'name', 'label': 'Center Name'},
            {'id': 'partner__name', 'label': 'Partner Name'},
            {'id': 'governorate__name', 'label': 'Governorate'},
            {'id': 'caza__name', 'label': 'Caza'},
            {'id': 'cadaster__name', 'label': 'Cadaster'},
            {'id': 'type', 'label': 'Center Type'},
            {'id': 'total_teachers', 'label': 'Total Teachers'},
            {'id': 'total_children', 'label': 'Total Children'},
        ]

        teacher_fields = [
            {'id': 'id', 'label': 'Teacher ID'},
            {'id': 'first_name', 'label': 'First Name'},
            {'id': 'last_name', 'label': 'Last Name'},
            {'id': 'gender', 'label': 'Gender'},
            {'id': 'center__name', 'label': 'Center Name'},
            {'id': 'center__partner__name', 'label': 'Partner Name'},
            {'id': 'round__name', 'label': 'Round Name'},
            {'id': 'phone_number', 'label': 'Phone Number'},
            {'id': 'email', 'label': 'Email'},
        ]

        # Filters
        partners = PartnerOrganization.objects.all()
        centers = Center.objects.all()
        rounds = Round.objects.all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                partners = partners.filter(id=user.partner_id)
                centers = centers.filter(partner_id=user.partner_id)
            if user.center_id:
                centers = centers.filter(id=user.center_id)

        context.update({
            'registration_fields': registration_fields,
            'center_fields': center_fields,
            'teacher_fields': teacher_fields,
            'partners': partners,
            'centers': centers,
            'rounds': rounds,
        })
        return context

@login_required(login_url='/users/login')
def queue_advanced_export(request):
    """API endpoint to trigger an advanced export background task."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    base_model = payload.get('base_model')
    if base_model not in ['registration', 'center', 'teacher']:
        return JsonResponse({'error': 'Invalid base model selected'}, status=400)

    fields = payload.get('fields', [])
    filters = payload.get('filters', {})
    file_format = payload.get('format', 'csv')

    # Create ExportHistory record
    export_record = ExportHistory.objects.create(
        export_type=f'Advanced Export ({base_model.capitalize()})',
        created_by=request.user,
        partner_name=request.user.partner.name if request.user.partner else '',
        fields={'base_model': base_model, 'fields': fields, 'filters': filters},
        file_format=file_format,
    )

    # Queue background task
    executor = _get_executor()
    executor.submit(
        _run_with_new_db_connection,
        _generate_advanced_export,
        export_record.id,
        base_model,
        fields,
        filters,
        file_format,
    )

    return JsonResponse({'status': 'started', 'export_id': export_record.id})
