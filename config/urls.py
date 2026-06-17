# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.static import static
from django.contrib import admin

# Customize Django admin site appearance
admin.site.site_header = "BMA"
admin.site.site_title = "BMA"
admin.site.index_title = "BMA"
admin.site.site_url = "/"
from django.views.generic import TemplateView
from django.views import defaults as default_views

from rest_framework_nested import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from student_registration.students.views import (
    TeacherViewSet
)
from student_registration.schools.views import (
    SchoolViewSet,
    SectionViewSet,
    SchoolAutocomplete
)

from student_registration.locations.views import (
    LocationViewSet,
    LocationAutocomplete
)

from student_registration.users.views import home, login_success, LandingPage, save_fcm_token
from student_registration.students.views import serve_file

from student_registration.mscc.api_views import (
    SyncSchoolViewSet,
    SyncTeacherViewSet,
    SyncRegistrationViewSet,
    SyncAttendanceViewSet
)


from student_registration.mscc.api_views import (
    SyncEducationProgrammeAssessmentViewSet,
    SyncFollowUpServiceViewSet
)

from student_registration.mscc.attendance_views import AttendanceHeatmapViewSet

api = routers.SimpleRouter()

# api.register(r'students', StudentViewSet, basename='students')
# api.register(r'students-search', StudentSearchViewSet, basename='students-search')
api.register(r'schools', SchoolViewSet, basename='schools')
api.register(r'sections', SectionViewSet, basename='sections')
api.register(r'teacher', TeacherViewSet, basename='teacher')
api.register(r'attendance-heatmap-data', AttendanceHeatmapViewSet, basename='attendance-heatmap-data')
api.register(r'locations', LocationViewSet, basename='locations')

api.register(r'sync/schools', SyncSchoolViewSet, basename='sync-schools')
api.register(r'sync/teachers', SyncTeacherViewSet, basename='sync-teachers')
api.register(r'sync/registrations', SyncRegistrationViewSet, basename='sync-registrations')
api.register(r'sync/attendances', SyncAttendanceViewSet, basename='sync-attendances')

api.register(r'sync/education-assessments', SyncEducationProgrammeAssessmentViewSet, basename='sync-education-assessments')
api.register(r'sync/followup-services', SyncFollowUpServiceViewSet, basename='sync-followup-services')



urlpatterns = [
    re_path(r'^$', home, name="home"),
    # re_path(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    re_path(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    re_path(r'^login-success/$', login_success, name='login_success'),
    re_path(r'^landing-page/$', LandingPage.as_view(), name='landing_page'),
    # re_path(r'^student-autocomplete/$', StudentAutocomplete.as_view(), name='student_autocomplete'),
    re_path(r'^school-autocomplete/$', SchoolAutocomplete.as_view(), name='school_autocomplete'),
    re_path(r'^location-autocomplete/$', LocationAutocomplete.as_view(), name='location_autocomplete'),

    # Django Admin, use {% url 'admin:index' %}
    re_path(settings.ADMIN_URL, admin.site.urls),

    # User management
    re_path(r'^users/', include('student_registration.users.urls', namespace='users')),
    re_path(r'^accounts/', include('allauth.urls')),

    re_path(r'^students/', include('student_registration.students.urls', namespace='students')),
    re_path(r'^clm/', include('student_registration.clm.urls', namespace='clm')),
    re_path(r'^mscc/', include('student_registration.mscc.urls', namespace='mscc')),
    re_path(r'^attendances/', include('student_registration.attendances.urls', namespace='attendances')),
    re_path(r'^schools/', include('student_registration.schools.urls', namespace='schools')),
    re_path(r'^locations/', include('student_registration.locations.urls', namespace='locations')),
    re_path(r'^dashboard/', include('student_registration.dashboard.urls', namespace='dashboard')),
    re_path(r'^backends/', include('student_registration.backends.urls', namespace='backends')),

    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # drf-spectacular URLs
    re_path(r'^api/schema/$', SpectacularAPIView.as_view(), name='schema'),
    re_path(r'^api/docs/$', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^api/schema/redoc/$', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    re_path(r'^api/save-fcm-token/$', save_fcm_token, name='save_fcm_token'),
    re_path(r'^api/', include(api.urls)),
    re_path(r"^serve-file/(?P<file_path>.+)/$", serve_file, name="serve_file"),
    re_path(r"^i18n/", include("django.conf.urls.i18n")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    import debug_toolbar
    urlpatterns += [
        re_path(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        re_path(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
