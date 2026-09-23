from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class DataQualityConfig(AppConfig):
    name = "student_registration.data_quality"
    verbose_name = _("Data quality")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from .permissions import ensure_reviewer_group
        from . import rules  # noqa: F401

        post_migrate.connect(
            ensure_reviewer_group,
            sender=self,
            dispatch_uid="data_quality.ensure_reviewer_group",
        )
