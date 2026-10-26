# -*- coding: utf-8 -*-
"""In-app access to the illustrated end-user manuals (``docs/user_manuals/``).

Every signed-in user can open ``/dashboard/manual/``. The page serves the manual
of the module that matches the account (ALP school users get the ALP manual,
everybody else the NFE manual) in the language of the interface, and offers the
Word and PDF files for download. Users may switch to the other module's manual
with the tabs at the top of the page.
"""
from __future__ import absolute_import, unicode_literals

import os
import re

import bleach
import markdown
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import TemplateView

from student_registration.users.templatetags.custom_tags import has_group

#: Module slug -> (file prefix, label shown in the page tabs).
MANUAL_MODULES = {
    'nfe': ('NFE', _('NFE module')),
    'alp': ('ALP', _('ALP module')),
    'admin': ('Admin', _('Admin panel')),
}
#: Manuals reserved for accounts that can open the admin panel.
STAFF_ONLY_MODULES = frozenset({'admin'})
MANUAL_LANGUAGES = ('en', 'ar')
MANUAL_FORMATS = {
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'pdf': 'application/pdf',
}
SCREENSHOT_NAME = re.compile(r'^[\w\-]+\.png$')


def user_manual_dir():
    """Absolute path of ``docs/user_manuals``."""
    return str(settings.ROOT_DIR.path('docs').path('user_manuals'))


def manual_module_for(user):
    """Return the manual module that matches the user's role."""
    if has_group(user, 'ALP_SCHOOL'):
        return 'alp'
    return 'nfe'


def user_can_read_manual(user, module):
    """Staff-only manuals (the admin panel manual) need staff or superuser status."""
    if module not in MANUAL_MODULES:
        return False
    if module in STAFF_ONLY_MODULES:
        return bool(user.is_staff or user.is_superuser)
    return True


def manual_language():
    """Return the manual language for the active interface language."""
    language = (get_language() or 'en').split('-')[0]
    return language if language in MANUAL_LANGUAGES else 'en'


def manual_markdown_path(module, language):
    prefix = MANUAL_MODULES[module][0]
    return os.path.join(user_manual_dir(), language, '%s_User_Manual.md' % prefix)


def manual_file_path(module, language, fmt):
    prefix = MANUAL_MODULES[module][0]
    return os.path.join(user_manual_dir(), '%s_User_Manual_%s.%s' % (prefix, language.upper(), fmt))


ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'dd', 'del', 'div', 'dl', 'dt', 'em',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p', 'pre', 's',
    'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'u', 'ul',
]
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'title'],
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan', 'scope'],
}


def render_manual(module, language):
    """Return the sanitized HTML of a manual, with screenshot links rewritten to the app route."""
    path = manual_markdown_path(module, language)
    if not os.path.exists(path):
        raise Http404('Manual not found')
    with open(path, 'r', encoding='utf-8') as fh:
        text = fh.read()
    # The Markdown wraps Arabic text in a <div dir="rtl">; the page sets the direction itself.
    text = re.sub(r'^<div dir="rtl">\s*|\s*</div>\s*$', '', text.strip())
    html_text = markdown.markdown(text, extensions=['extra', 'toc'])

    def rewrite_image(match):
        name = match.group(2)
        if not SCREENSHOT_NAME.match(name):
            return match.group(0)
        url = reverse('dashboard:user_manual_screenshot', args=[language, name])
        return 'src="%s" loading="lazy"' % url

    html_text = re.sub(r'src="\.\./screenshots/(en|ar)/([^"]+)"', rewrite_image, html_text)
    return mark_safe(bleach.clean(html_text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True))


class UserManualView(LoginRequiredMixin, TemplateView):
    template_name = 'wiki/user_manual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.kwargs.get('module') or manual_module_for(self.request.user)
        if not user_can_read_manual(self.request.user, module):
            raise Http404('Manual not found')
        language = manual_language()
        context['manual_content'] = render_manual(module, language)
        context['module'] = module
        context['module_label'] = MANUAL_MODULES[module][1]
        context['language'] = language
        context['is_rtl'] = language == 'ar'
        context['modules'] = [
            {'slug': slug, 'label': label, 'active': slug == module,
             'url': reverse('dashboard:user_manual_module', args=[slug])}
            for slug, (_prefix, label) in MANUAL_MODULES.items()
            if user_can_read_manual(self.request.user, slug)
        ]
        context['downloads'] = [
            {'format': fmt, 'url': reverse('dashboard:user_manual_download', args=[module, language, fmt]),
             'available': os.path.exists(manual_file_path(module, language, fmt))}
            for fmt in MANUAL_FORMATS
        ]
        return context


@login_required
def user_manual_screenshot(request, language, name):
    """Serve one manual screenshot to a signed-in user."""
    if language not in MANUAL_LANGUAGES or not SCREENSHOT_NAME.match(name):
        raise Http404('Screenshot not found')
    path = os.path.join(user_manual_dir(), 'screenshots', language, name)
    if not os.path.isfile(path):
        raise Http404('Screenshot not found')
    return FileResponse(open(path, 'rb'), content_type='image/png')


@login_required
def user_manual_download(request, module, language, fmt):
    """Send the Word or PDF version of a manual as an attachment."""
    if (not user_can_read_manual(request.user, module) or language not in MANUAL_LANGUAGES
            or fmt not in MANUAL_FORMATS):
        raise Http404('Manual not found')
    path = manual_file_path(module, language, fmt)
    if not os.path.isfile(path):
        raise Http404('Manual not found')
    return FileResponse(
        open(path, 'rb'), content_type=MANUAL_FORMATS[fmt],
        as_attachment=True, filename=os.path.basename(path),
    )
