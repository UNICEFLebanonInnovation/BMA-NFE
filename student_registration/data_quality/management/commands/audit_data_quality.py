from django.core.management.base import BaseCommand, CommandError

from student_registration.child.models import Child
from student_registration.data_quality.services import MonitorOnlyEvaluationService
from student_registration.mscc.models import Registration


MODEL_CONFIG = {
    "child": (
        Child,
        lambda: Child.objects.select_related("nationality", "disability").all(),
    ),
    "registration": (
        Registration,
        lambda: Registration.objects.select_related("child", "partner", "center").all(),
    ),
}


class Command(BaseCommand):
    help = "Run monitor-only data-quality rules for MSCC children or registrations."

    def add_arguments(self, parser):
        parser.add_argument("--model", choices=MODEL_CONFIG, required=True)
        selection = parser.add_mutually_exclusive_group(required=True)
        selection.add_argument("--record-id", type=int)
        selection.add_argument(
            "--all",
            action="store_true",
            help="Audit every record for the selected model.",
        )

    def handle(self, *args, **options):
        model_name = options["model"]
        model, queryset_factory = MODEL_CONFIG[model_name]
        queryset = queryset_factory()
        record_id = options.get("record_id")
        if record_id is not None:
            queryset = queryset.filter(pk=record_id)
            if not queryset.exists():
                raise CommandError(
                    f"{model.__name__} with ID {record_id} does not exist."
                )

        scope = {
            "model": model_name,
            "record_id": record_id,
            "all_records": bool(options.get("all")),
        }
        quality_run = MonitorOnlyEvaluationService().run(
            subjects=queryset.iterator(),
            scope=scope,
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Data-quality run {run_id} completed: {records} records, "
                "{rules} evaluations, {failures} findings (monitor only).".format(
                    run_id=quality_run.pk,
                    records=quality_run.records_checked,
                    rules=quality_run.rules_evaluated,
                    failures=quality_run.failures_found,
                )
            )
        )
