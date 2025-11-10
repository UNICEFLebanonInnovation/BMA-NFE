from celery import signals
from django.utils import timezone

from .models import TaskRunLog


@signals.task_prerun.connect
def log_task_start(sender=None, task_id=None, task=None, **kwargs):
    TaskRunLog.objects.create(task_id=task_id, task_name=sender.name, status="STARTED")


@signals.task_postrun.connect
def log_task_success(sender=None, task_id=None, retval=None, **kwargs):
    TaskRunLog.objects.filter(task_id=task_id).update(
        status="SUCCESS", finished_at=timezone.now(), result=str(retval)[:1000]
    )


@signals.task_failure.connect
def log_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    TaskRunLog.objects.filter(task_id=task_id).update(
        status="FAILURE", finished_at=timezone.now(), result=str(exception)
    )
