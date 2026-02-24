# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, FormView
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from .models import User, WebPushToken
from student_registration.mscc.models import Registration
from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.backends.models import ExportHistory
import json


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserChangeLanguageRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False
    query_string = True
    pattern_name = 'set_language'

    def get_redirect_url(self, *args, **kwargs):
        # user_language = kwargs['language']
        # translation.activate(user_language)
        # self.request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        return reverse('home')


def login_success(request):
    """
    Redirects users based on whether they are in the admins group
    """

    # if has_group(request.user, 'MSCC'):
    #     return HttpResponseRedirect(reverse('mscc:list'))
    # elif has_group(request.user, 'YOUTH'):
    #     return HttpResponseRedirect(reverse('youth:list'))
    # elif has_group(request.user, 'CLM_Inclusion'):
    #     return HttpResponseRedirect(reverse('clm:inclusion_list'))
    # else:
    #     return HttpResponseRedirect(reverse('clm:bridging_page'))

    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    user = request.user
    modules = []

    # MSCC access
    if user.is_superuser or user.groups.filter(name__in=[
        'MSCC_UNICEF', 'MSCC_PARTNER', 'MSCC_CENTER', 'MSCC'
    ]).exists():
        modules.append('mscc')

    # Dirasa / Bridging
    if user.is_superuser or user.groups.filter(name='CLM_Bridging').exists():
        modules.append('clm_bridging')

    # Disability specialized inclusion
    if user.is_superuser or user.groups.filter(name='CLM_Inclusion').exists():
        modules.append('clm_inclusion')

    # Youth
    if user.is_superuser or user.groups.filter(name__in=[
        'YOUTH_UNICEF', 'YOUTH_PARTNER', 'YOUTH'
    ]).exists():
        modules.append('youth')

    if len(modules) == 1:
        module = modules[0]
        if module == 'mscc':
            return redirect('mscc:list')
        if module == 'clm_bridging':
            return redirect('clm:bridging_page')
        if module == 'clm_inclusion':
            return redirect('clm:inclusion_list')
        if module == 'youth':
            return redirect('youth:list')

    # Default to landing page if multiple modules or no specific match
    return redirect('/landing-page/')


class LandingPage(LoginRequiredMixin,
                   TemplateView):
    template_name = 'landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if settings.USE_TZ:
            today = timezone.localdate()
        else:
            today = timezone.now().date()
        week_start = today - timezone.timedelta(days=6)
        trend_start = today - timezone.timedelta(days=13)
        month_start = today.replace(day=1)

        registrations = Registration.objects.filter(deleted=False)

        today_count = registrations.filter(created__date=today).count()
        week_count = registrations.filter(created__date__gte=week_start).count()
        active_learners = registrations.values('child_id').distinct().count()
        pending_validation = registrations.filter(
            Q(child__birthday__isnull=True)
            | Q(child__gender__isnull=True)
            | Q(child__nationality__isnull=True)
        ).count()
        centers_reporting = registrations.filter(
            created__date__gte=today - timezone.timedelta(days=30),
            center__isnull=False,
        ).values('center_id').distinct().count()

        attendance_rows = MSCCAttendanceChild.objects.filter(
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
            day = trend_start + timezone.timedelta(days=idx)
            key = day.strftime('%Y-%m-%d')
            trend_data.append({'date': key, 'value': trend_map.get(key, 0)})

        top_centers_qs = (
            registrations.filter(center__isnull=False)
            .values('center__name')
            .annotate(value=Count('id'))
            .order_by('-value')[:8]
        )
        top_centers = [
            {'name': row['center__name'] or 'Unknown Center', 'value': row['value']}
            for row in top_centers_qs
        ]

        recent_exports = ExportHistory.objects.filter(
            export_type__icontains='Makani'
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
            })

        context.update({
            'kpi_today': today_count,
            'kpi_week': week_count,
            'kpi_active': active_learners,
            'kpi_pending': pending_validation,
            'kpi_centers': centers_reporting,
            'kpi_attendance': attendance_percent,
            'trend_data': json.dumps(trend_data),
            'top_centers_data': json.dumps(top_centers),
            'recent_exports': export_rows,
        })
        return context


def home(request):

    if request.user.is_authenticated:
        return redirect('/login-success/')
    else:
        return redirect('/accounts/login/')


def user_overview(request):

    args = {
        'user': request.user,
               }
    return render(request, 'users/profile.html', args)


@csrf_exempt
@require_POST
@login_required
def save_fcm_token(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = data.get('token')
    except (ValueError, KeyError):
        return HttpResponseBadRequest('Invalid payload')
    if not token:
        return HttpResponseBadRequest('Missing token')
    token_obj, _ = WebPushToken.objects.get_or_create(
        token=token,
        defaults={'user': request.user}
    )
    if token_obj.user != request.user:
        token_obj.user = request.user
        token_obj.save(update_fields=["user"])
    WebPushToken.objects.filter(user=request.user).exclude(pk=token_obj.pk).delete()
    return JsonResponse({'status': 'ok'})
