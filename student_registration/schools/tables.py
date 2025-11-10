# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import School, Club, Meeting, CommunityInitiative, HealthVisit


class SchoolTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit school'), orderable=False,
                                        template_name='django_tables2/school_edit_column.html',
                                        attrs={'url': '/schools/school-edit/', 'programme': 'Bridging'})
    club_column = tables.TemplateColumn(verbose_name=_('Clubs'), orderable=False,
                                        template_name='django_tables2/school/club_list_column.html',
                                        attrs={'url': '/schools/club-list/', 'programme': 'Bridging'})

    meeting_column = tables.TemplateColumn(verbose_name=_('Meetings'), orderable=False,
                                        template_name='django_tables2/school/meeting_list_column.html',
                                        attrs={'url': '/schools/meeting-list/', 'programme': 'Bridging'})

    community_initiative_column = tables.TemplateColumn(verbose_name=_('Community Initiatives'), orderable=False,
                                        template_name='django_tables2/school/community_initiative_list_column.html',
                                        attrs={'url': '/schools/community-initiative-list/', 'programme': 'Bridging'})

    health_visit_column = tables.TemplateColumn(verbose_name=_('Health Visits'), orderable=False,
                                        template_name='django_tables2/school/health_visit_list_column.html',
                                        attrs={'url': '/schools/health-visit-list/', 'programme': 'Bridging'})

    # delete_column = tables.TemplateColumn(verbose_name=_('Delete school'), orderable=False,
    #                                       template_name='django_tables2/school_delete_column.html',
    #                                       attrs={'url': '/api/school/', 'programme': 'Bridging'})

    class Meta:
        model = School
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'edit_column',
            'club_column',
            'meeting_column',
            'community_initiative_column',
            'health_visit_column',
            'governorate',
            'number',
            'name',
            'director_name',
            'land_phone_number',
            'email',
            'is_closed',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class SchoolExportTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit school'), orderable=False,
                                        template_name='django_tables2/school_edit_column.html',
                                        attrs={'url': '/schools/school-edit/', 'programme': 'Bridging'})
    club_column = tables.TemplateColumn(verbose_name=_('Clubs'), orderable=False,
                                        template_name='django_tables2/school/club_list_column.html',
                                        attrs={'url': '/schools/club-list/', 'programme': 'Bridging'})

    meeting_column = tables.TemplateColumn(verbose_name=_('Meetings'), orderable=False,
                                        template_name='django_tables2/school/meeting_list_column.html',
                                        attrs={'url': '/schools/meeting-list/', 'programme': 'Bridging'})

    community_initiative_column = tables.TemplateColumn(verbose_name=_('Community Initiatives'), orderable=False,
                                        template_name='django_tables2/school/community_initiative_list_column.html',
                                        attrs={'url': '/schools/community-initiative-list/', 'programme': 'Bridging'})

    health_visit_column = tables.TemplateColumn(verbose_name=_('Health Visits'), orderable=False,
                                        template_name='django_tables2/school/health_visit_list_column.html',
                                        attrs={'url': '/schools/health-visit-list/', 'programme': 'Bridging'})

    bridging_export_column = tables.TemplateColumn(verbose_name=_('Dirasa Data'), orderable=False,
                                        template_name='django_tables2/school/bridging_export_column.html',
                                        attrs={'url': '/clm/bridging-school-export-data/', 'programme': 'Bridging'})

    # delete_column = tables.TemplateColumn(verbose_name=_('Delete school'), orderable=False,
    #                                       template_name='django_tables2/school_delete_column.html',
    #                                       attrs={'url': '/api/school/', 'programme': 'Bridging'})

    class Meta:
        model = School
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'edit_column',
            'club_column',
            'meeting_column',
            'community_initiative_column',
            'health_visit_column' ,
            'bridging_export_column',
            'governorate',
            'number',
            'name',
            'director_name',
            'land_phone_number',
            'email',
            'is_closed',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class ClubTable(tables.Table):

    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                        template_name='django_tables2/school/club_action_column.html',
                                        attrs={'url_edit': '/schools/club-edit/',
                                               'url_delete': '/schools/club-delete/',
                                               'programme': 'Bridging'})

    class Meta:
        model = Club
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'action_column',
            'club_name',
            'number_clubs',
            'club_type',
            'number_children',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class MeetingTable(tables.Table):

    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                        template_name='django_tables2/school/meeting_action_column.html',
                                        attrs={'url_edit': '/schools/meeting-edit/',
                                               'url_delete': '/schools/meeting-delete/',
                                               'programme': 'Bridging'})

    class Meta:
        model = Meeting
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'action_column',
            'meeting_name',
            'meeting_date',
            'number_participants',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class CommunityInitiativeTable(tables.Table):

    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                        template_name='django_tables2/school/initiative_action_column.html',
                                        attrs={'url_edit': '/schools/community-initiative-edit/',
                                               'url_delete': '/schools/community-initiative-delete/',
                                               'programme': 'Bridging'})

    class Meta:
        model = CommunityInitiative
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'action_column',
            'community_group_name',
            'number_initiatives',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class HealthVisitTable(tables.Table):

    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                        template_name='django_tables2/school/visit_action_column.html',
                                        attrs={'url_edit': '/schools/health-visit-edit/',
                                               'url_delete': '/schools/health-visit-delete/',
                                               'programme': 'Bridging'})

    class Meta:
        model = HealthVisit
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'action_column',
            'focal_point_name',
            'number_visits',
            'date_first_visit',
            'date_last_visit',
            'owner',
            'modified_by',
            'created',
            'modified',
        )
