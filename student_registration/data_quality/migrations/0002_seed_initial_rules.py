from django.db import migrations


INITIAL_RULES = (
    ("DQ-BIRTH-001", "Birth date is complete and valid", "error"),
    ("DQ-BIRTH-002", "Birth date is not in the future", "error"),
    ("DQ-ID-001", "Identity values match their confirmations", "error"),
    ("DQ-PHONE-001", "Phone values match their confirmations", "error"),
    ("DQ-NATIONALITY-001", "Other nationality has explanatory text", "warning"),
    ("DQ-DISABILITY-001", "Other disability has explanatory text", "warning"),
    ("DQ-CHILDREN-001", "No children has a zero or empty count", "warning"),
    ("DQ-CHILDREN-002", "Having children has a positive count", "warning"),
    ("DQ-CASH-001", "None is not combined with another cash programme", "warning"),
    ("DQ-RELATION-001", "Registration partner and center are consistent", "error"),
    ("DQ-RELATION-002", "Registration has a child", "error"),
)


def seed_rules(apps, schema_editor):
    DataQualityRule = apps.get_model("data_quality", "DataQualityRule")
    for code, name, severity in INITIAL_RULES:
        DataQualityRule.objects.update_or_create(
            code=code,
            version=1,
            defaults={
                "name": name,
                "severity": severity,
                "status": "monitoring",
                "description": "Initial monitor-only MSCC data-quality rule.",
            },
        )


def remove_rules(apps, schema_editor):
    DataQualityRule = apps.get_model("data_quality", "DataQualityRule")
    DataQualityRule.objects.filter(
        code__in=[rule[0] for rule in INITIAL_RULES],
        version=1,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("data_quality", "0001_initial")]

    operations = [migrations.RunPython(seed_rules, remove_rules)]
