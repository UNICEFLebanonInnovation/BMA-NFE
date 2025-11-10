from django.contrib import admin
from .models import TaskRunLog



@admin.register(TaskRunLog)
class TaskRunLogAdmin(admin.ModelAdmin):
    list_display = ("task_name", "status", "started_at", "finished_at")
    search_fields = ("task_name", "task_id")
