from datetime import date

from student_registration.child.models import Child
from student_registration.data_quality.registry import registry

from .base import DeterministicRule


DATE_FIELDS = ("birthday_year", "birthday_month", "birthday_day")
IDENTITY_CONFIRMATION_PAIRS = (
    ("case_number", "case_number_confirm"),
    ("parent_individual_case_number", "parent_individual_case_number_confirm"),
    ("individual_case_number", "individual_case_number_confirm"),
    ("recorded_number", "recorded_number_confirm"),
    ("parent_national_number", "parent_national_number_confirm"),
    ("national_number", "national_number_confirm"),
    ("parent_extract_record", "parent_extract_record_confirm"),
    ("parent_syrian_national_number", "parent_syrian_national_number_confirm"),
    ("syrian_national_number", "syrian_national_number_confirm"),
    ("parent_sop_national_number", "parent_sop_national_number_confirm"),
    ("sop_national_number", "sop_national_number_confirm"),
    ("parent_other_number", "parent_other_number_confirm"),
    ("other_number", "other_number_confirm"),
)
PHONE_CONFIRMATION_PAIRS = (
    ("first_phone_number", "first_phone_number_confirm"),
    ("second_phone_number", "second_phone_number_confirm"),
)


def _is_empty(value):
    return value in (None, "", 0, "0")


def _birth_date(child):
    if any(_is_empty(getattr(child, field)) for field in DATE_FIELDS):
        return None
    try:
        return date(
            int(child.birthday_year),
            int(child.birthday_month),
            int(child.birthday_day),
        )
    except (TypeError, ValueError):
        return None


def _mismatched_pairs(subject, pairs):
    mismatches = []
    for value_field, confirmation_field in pairs:
        value = getattr(subject, value_field)
        confirmation = getattr(subject, confirmation_field)
        if not _is_empty(value) and value != confirmation:
            mismatches.append((value_field, confirmation_field))
    return mismatches


@registry.register
class BirthDateIsRealRule(DeterministicRule):
    rule_code = "DQ-BIRTH-001"
    model = Child

    def __call__(self, child):
        missing_fields = [
            field for field in DATE_FIELDS if _is_empty(getattr(child, field))
        ]
        valid = not missing_fields and _birth_date(child) is not None
        reason = "missing_components" if missing_fields else "invalid_calendar_date"
        return self.result(
            valid,
            affected_fields=DATE_FIELDS,
            evidence={"reason": reason, "missing_fields": missing_fields},
            message_code="data_quality.birth_date_invalid",
        )


@registry.register
class BirthDateNotFutureRule(DeterministicRule):
    rule_code = "DQ-BIRTH-002"
    model = Child

    def __call__(self, child):
        birth_date = _birth_date(child)
        passed = birth_date is None or birth_date <= date.today()
        return self.result(
            passed,
            affected_fields=DATE_FIELDS,
            evidence={"reason": "future_date"} if not passed else {},
            message_code="data_quality.birth_date_future",
        )


class ConfirmationRule(DeterministicRule):
    pairs = ()
    message_code = ""

    def __call__(self, child):
        mismatches = _mismatched_pairs(child, self.pairs)
        affected_fields = [field for pair in mismatches for field in pair]
        return self.result(
            not mismatches,
            affected_fields=affected_fields,
            evidence={"mismatched_pairs": [list(pair) for pair in mismatches]},
            message_code=self.message_code,
        )


@registry.register
class IdentityConfirmationRule(ConfirmationRule):
    rule_code = "DQ-ID-001"
    model = Child
    pairs = IDENTITY_CONFIRMATION_PAIRS
    message_code = "data_quality.identity_confirmation_mismatch"


@registry.register
class PhoneConfirmationRule(ConfirmationRule):
    rule_code = "DQ-PHONE-001"
    model = Child
    pairs = PHONE_CONFIRMATION_PAIRS
    message_code = "data_quality.phone_confirmation_mismatch"


@registry.register
class NationalityOtherRequiredRule(DeterministicRule):
    rule_code = "DQ-NATIONALITY-001"
    model = Child

    def __call__(self, child):
        nationality_name = (
            (child.nationality.name_en or child.nationality.name).strip().casefold()
            if child.nationality
            else ""
        )
        applies = nationality_name == "other"
        passed = not applies or bool((child.nationality_other or "").strip())
        return self.result(
            passed,
            affected_fields=("nationality_other",) if not passed else (),
            evidence={"reason": "other_value_requires_detail"} if not passed else {},
            message_code="data_quality.nationality_other_required",
        )


@registry.register
class DisabilityOtherRequiredRule(DeterministicRule):
    rule_code = "DQ-DISABILITY-001"
    model = Child

    def __call__(self, child):
        disability_name = (
            (child.disability.name_en or child.disability.name).strip().casefold()
            if child.disability
            else ""
        )
        applies = disability_name == "other" or disability_name == "غير ذلك"
        passed = not applies or bool((child.disability_other or "").strip())
        return self.result(
            passed,
            affected_fields=("disability_other",) if not passed else (),
            evidence={"reason": "other_value_requires_detail"} if not passed else {},
            message_code="data_quality.disability_other_required",
        )


@registry.register
class ChildCountZeroRule(DeterministicRule):
    rule_code = "DQ-CHILDREN-001"
    model = Child

    def __call__(self, child):
        applies = child.have_children == "No"
        passed = not applies or child.children_number in (None, 0)
        return self.result(
            passed,
            affected_fields=("have_children", "children_number") if not passed else (),
            evidence={"reason": "no_children_requires_zero"} if not passed else {},
            message_code="data_quality.children_count_must_be_zero",
        )


@registry.register
class ChildCountPositiveRule(DeterministicRule):
    rule_code = "DQ-CHILDREN-002"
    model = Child

    def __call__(self, child):
        applies = child.have_children in (
            "Yes",
            "Child pregnant or expecting children",
        )
        passed = not applies or bool(
            child.children_number is not None and child.children_number > 0
        )
        return self.result(
            passed,
            affected_fields=("have_children", "children_number") if not passed else (),
            evidence={"reason": "children_requires_positive_count"} if not passed else {},
            message_code="data_quality.children_count_must_be_positive",
        )
