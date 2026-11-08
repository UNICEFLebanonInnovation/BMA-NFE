"""Production media and readiness routes used only by the MEHE profile."""
from django.urls import re_path
from config.urls import urlpatterns as application_urls
from student_registration.mehe_views import child_photo, readiness
urlpatterns = [
    re_path(r'^media/(?P<name>.+)$', child_photo, name='mehe-child-photo'),
    re_path(r'^health/ready/$', readiness, name='mehe-readiness'),
] + application_urls
