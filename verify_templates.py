import os
import django
from django.conf import settings
from django.template.loader import render_to_string

# Minimal settings to render templates
if not settings.configured:
    settings.configure(
        DEBUG=True,
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(os.getcwd(), 'student_registration', 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                'libraries': {
                    'custom_tags': 'student_registration.mscc.templatetags.custom_tags',
                    'util_tags': 'student_registration.mscc.templatetags.util_tags',
                    'simple_tags': 'student_registration.mscc.templatetags.simple_tags',
                }
            },
        }],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.messages',
            'django.contrib.sessions',
            'django.contrib.admin',
            'django.contrib.staticfiles',
            'django.contrib.sites',
            'django_bootstrap5',
            'crispy_forms',
            'crispy_bootstrap5',
            'student_registration.mscc',
            'student_registration.dashboard',
            'student_registration.accounts',
            'student_registration.users',
            'student_registration.students',
            'student_registration.child',
            'student_registration.locations',
            'student_registration.attendances',
            'student_registration.schools',
            'student_registration.clm',
        ],
        STATIC_URL='/static/',
        CRISPY_ALLOWED_TEMPLATE_PACKS="bootstrap5",
        CRISPY_TEMPLATE_PACK="bootstrap5",
        SITE_ID=1,
    )
    django.setup()

def verify_render(template_name, context_dict, output_file):
    try:
        html = render_to_string(template_name, context_dict)
        with open(output_file, 'w') as f:
            f.write(html)
        print(f"Successfully rendered {template_name} to {output_file}")
    except Exception as e:
        import traceback
        print(f"Error rendering {template_name}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    context = {
        'request': type('MockRequest', (), {
            'user': type('MockUser', (), {
                'is_authenticated': True,
                'username': 'jules',
                'first_name': 'Jules',
                'get_full_name': lambda self: 'Jules Engineer'
            })(),
            'path': '/',
            'resolver_match': type('MockMatch', (), {'url_name': 'home'})()
        })(),
        'kpi_today': 5,
        'kpi_week': 25,
        'kpi_active': 1200,
        'kpi_pending': 12,
        'kpi_centers': 45,
        'kpi_attendance': 88,
        'recent_exports': [],
        'trend_data': '[]',
        'top_centers_data': '[]',
    }
    verify_render('landing_page.html', context, 'landing_rendered.html')
