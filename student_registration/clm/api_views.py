# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from openpyxl import Workbook

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, Sum, Avg, F, Func, When
from django.db.models.expressions import RawSQL
from django.urls import reverse
from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

from .models import (
    Bridging
)
from student_registration.students.models import Teacher
from student_registration.students.serializers import TeacherSerializer
from student_registration.schools.models import (
    CLMRound,
    School,
    PartnerOrganization,
)
from student_registration.schools.serializers import SchoolSerializer
from .serializers import (
    BridgingSerializer
)
from student_registration.attendances.models import CLMAttendance, CLMAttendanceStudent
from student_registration.attendances.serializers import CLMAttendanceStudentSerializer
from student_registration.users.templatetags.custom_tags import has_group


class BridgingListViewSet(viewsets.ModelViewSet):

    queryset = Bridging.objects.all()
    serializer_class = BridgingSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = Bridging.objects.none()
        if self.request.user.partner:
            qs = Bridging.objects.filter(partner_id=self.request.user.partner_id)
            if self.request.user.school:
                qs = qs.filter(school_id=self.request.user.school_id)

        return qs


class SchoolListViewSet(viewsets.ModelViewSet):

    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = School.objects.all()
        if self.request.user.partner:
            qs = School.objects.filter(is_closed=False,
                                       id__in=PartnerOrganization
                                       .objects
                                       .filter(id=self.request.user.partner_id)
                                       .values_list('schools', flat=True))
        else:
            qs = qs.none()

        return qs


class TeacherListViewSet(viewsets.ModelViewSet):

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = Teacher.objects.all()
        if self.request.user.partner:
            qs = Teacher.objects.filter(school_id__in=PartnerOrganization
                                        .objects
                                        .filter(id=self.request.user.partner_id)
                                        .values_list('schools', flat=True))
        else:
            qs = qs.none()

        return qs


class AttendanceListViewSet(viewsets.ModelViewSet):
    queryset = CLMAttendanceStudent.objects.all()
    serializer_class = CLMAttendanceStudentSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = CLMAttendanceStudent.objects.none()
        if self.request.user.partner:
            qs = CLMAttendanceStudent.objects.filter(attendance_day__school_id__in=PartnerOrganization.objects
                                                     .filter(id=self.request.user.partner_id)
                                                     .values_list('schools', flat=True))

        return qs
