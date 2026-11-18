from student_registration.data_quality.registry import registry
from student_registration.mscc.models import Registration

from .base import DeterministicRule


@registry.register
class CashProgrammeSelectionRule(DeterministicRule):
    rule_code = "DQ-CASH-001"
    model = Registration

    def __call__(self, registration):
        programmes = registration.cash_support_programmes or []
        passed = not ("None" in programmes and len(programmes) > 1)
        return self.result(
            passed,
            affected_fields=("cash_support_programmes",) if not passed else (),
            evidence={"reason": "none_selected_with_other_values"} if not passed else {},
            message_code="data_quality.cash_programmes_mutually_exclusive",
        )


@registry.register
class RegistrationPartnerCenterRule(DeterministicRule):
    rule_code = "DQ-RELATION-001"
    model = Registration

    def __call__(self, registration):
        missing_fields = [
            field
            for field in ("partner", "center")
            if getattr(registration, f"{field}_id") is None
        ]
        mismatch = bool(
            not missing_fields
            and registration.center.partner_id != registration.partner_id
        )
        passed = not missing_fields and not mismatch
        reason = "missing_relationship" if missing_fields else "partner_center_mismatch"
        return self.result(
            passed,
            affected_fields=(tuple(missing_fields) or ("partner", "center"))
            if not passed
            else (),
            evidence={"reason": reason, "missing_fields": missing_fields}
            if not passed
            else {},
            message_code="data_quality.registration_partner_center_invalid",
        )


@registry.register
class RegistrationChildRequiredRule(DeterministicRule):
    rule_code = "DQ-RELATION-002"
    model = Registration

    def __call__(self, registration):
        passed = registration.child_id is not None
        return self.result(
            passed,
            affected_fields=("child",) if not passed else (),
            evidence={"reason": "child_missing"} if not passed else {},
            message_code="data_quality.registration_child_required",
        )
