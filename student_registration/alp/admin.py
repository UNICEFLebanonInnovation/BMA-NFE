from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    ALPRound, ALPProgram, ALPTeacher, ALPRegistration,
    ALPGrading, ALPGradingDefinition, ALPTeacherAttendance, ALPAttendance
)

@admin.register(ALPRound)
class ALPRoundAdmin(ImportExportModelAdmin):
    list_display = ('name', 'current_year')

@admin.register(ALPProgram)
class ALPProgramAdmin(ImportExportModelAdmin):
    list_display = ('name',)

@admin.register(ALPTeacher)
class ALPTeacherAdmin(ImportExportModelAdmin):
    list_display = ('first_name', 'last_name', 'school', 'sex')
    search_fields = ('first_name', 'last_name', 'school__name')

@admin.register(ALPRegistration)
class ALPRegistrationAdmin(ImportExportModelAdmin):
    list_display = ('id', 'child', 'school', 'round', 'programme')
    search_fields = ('child__first_name', 'child__last_name', 'school__name')
    raw_id_fields = ('child', 'school', 'owner', 'modified_by')

@admin.register(ALPGrading)
class ALPGradingAdmin(ImportExportModelAdmin):
    list_display = ('registration',)

@admin.register(ALPGradingDefinition)
class ALPGradingDefinitionAdmin(ImportExportModelAdmin):
    list_display = ('material', 'min_grade', 'max_grade')

@admin.register(ALPTeacherAttendance)
class ALPTeacherAttendanceAdmin(ImportExportModelAdmin):
    list_display = ('teacher', 'date', 'status')
    search_fields = ('teacher__first_name', 'teacher__last_name')

@admin.register(ALPAttendance)
class ALPAttendanceAdmin(ImportExportModelAdmin):
    list_display = ('registration', 'date', 'status', 'shift')
    search_fields = ('registration__child__first_name', 'registration__child__last_name')
