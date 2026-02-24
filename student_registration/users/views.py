# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import reverse, reverse_lazy
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
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import User, WebPushToken
import json
from student_registration.mscc.models import Registration
from student_registration.users.templatetags.custom_tags import has_group


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

    def get_mscc_queryset(self):
        """Return registrations scoped by user role and current round context."""
        user = self.request.user
        queryset = Registration.objects.filter(deleted=False)
        round_filter = Q(round__isnull=True) | Q(round__current_year=True)

        if user.is_superuser or has_group(user, 'MSCC_UNICEF'):
            return queryset.filter(round_filter)

        if has_group(user, 'MSCC_PARTNER') and user.partner_id:
            return queryset.filter(round_filter, partner_id=user.partner_id)

        if has_group(user, 'MSCC_CENTER') and user.center_id:
            return queryset.filter(round_filter, center_id=user.center_id)

        if has_group(user, 'MSCC'):
            return queryset.filter(round_filter)

        return Registration.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_mscc_queryset()

        today = timezone.localdate()
        start_date = today - timedelta(days=13)

        trend_rows = (
            queryset.filter(created__date__gte=start_date, created__date__lte=today)
            .values('created__date')
            .annotate(value=Count('id'))
            .order_by('created__date')
        )
        trend_lookup = {
            row['created__date'].isoformat(): row['value']
            for row in trend_rows
            if row['created__date']
        }

        trend_data = []
        for offset in range(14):
            day = start_date + timedelta(days=offset)
            day_key = day.isoformat()
            trend_data.append({'date': day_key, 'value': trend_lookup.get(day_key, 0)})

        centers_data = list(
            queryset.filter(center__isnull=False)
            .values('center__name')
            .annotate(value=Count('id'))
            .order_by('-value', 'center__name')[:8]
        )
        centers_data = [
            {'name': row['center__name'], 'value': row['value']}
            for row in centers_data
            if row['center__name']
        ]

        context.update({
            'trend_data_json': json.dumps(trend_data),
            'centers_data_json': json.dumps(centers_data),
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
