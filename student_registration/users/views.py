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
from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from student_registration.alp.templatetags.util_tags import has_group
from student_registration.users.utils import force_default_language
from django.shortcuts import redirect, render
from .models import User, WebPushToken
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


def home(request):

    if request.user.is_authenticated:
        return redirect('/login-success/')
    else:
        return redirect('/accounts/login/')


class LoginRedirectView(LoginRequiredMixin, RedirectView):
    permanent = True

    def get_redirect_url(self):
        if has_group(self.request.user, 'SCHOOL') or has_group(self.request.user, 'ALP_SCHOOL'):
            return reverse('schools:profile', kwargs={})
        if has_group(self.request.user, 'CLM'):
            return reverse('clm:index', kwargs={})
        if has_group(self.request.user, 'HELPDESK'):
            return reverse('helpdesk_dashboard', kwargs={})
        return reverse('home')


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
