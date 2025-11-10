# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.utils.timezone import localtime

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin


from .exporter import export_full_data
from .models import Notification, Exporter, ExportHistory
from .serializers import NotificationSerializer, ExporterSerializer
from .filters import ExporterFilter
from .tables import BootstrapTable, ExporterTable


class NotificationViewSet(mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):

    model = Notification
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # def update(self, request, *args, **kwargs):
    #     if 'pk' not in kwargs:
    #         return super(NotificationViewSet, self).update(request)
    #     instance = self.model.objects.get(id=kwargs['pk'])
    #     print(request)
    #     instance.status = True
    #     instance.save()
    #     return JsonResponse({'status': status.HTTP_200_OK, 'data': instance.id})


class ExporterListView(LoginRequiredMixin,
                       FilterView,
                       ExportMixin,
                       SingleTableView,
                       RequestConfig):

    table_class = ExporterTable
    model = Exporter
    template_name = 'backends/files.html'
    table = BootstrapTable(Exporter.objects.all(), order_by='-id')

    filterset_class = ExporterFilter

    def get_queryset(self):
        return Exporter.objects.filter(exported_by=self.request.user)


class ExporterViewSet(LoginRequiredMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet,):

    model = Exporter
    queryset = Exporter.objects.all()
    serializer_class = ExporterSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def list(self, request, *args, **kwargs):
        if self.request.GET.get('report', None):
            #  todo raise a exception if the partner
            data = {
                'report': self.request.GET.get('report'),
                'user': self.request.user.id,
                'partner': self.request.user.partner_id
            }
            export_full_data(data)
        return JsonResponse({'status': status.HTTP_200_OK})


@login_required
def export_history_list(request):
    exports = (
        ExportHistory.objects.filter(created_by=request.user)
        .order_by('-created')[:5]
    )
    data = []
    for export in exports:
        timestamp = localtime(export.created).strftime('%Y-%m-%d %H:%M')
        data.append({'url': export.file_url or '#', 'text': f'MSCC export {timestamp}'})
    return JsonResponse({'exports': data})

