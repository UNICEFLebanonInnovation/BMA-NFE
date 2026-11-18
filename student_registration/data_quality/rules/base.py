from student_registration.data_quality.services import RuleEvaluation


class DeterministicRule:
    """Base contract for deterministic, side-effect-free rule evaluators."""

    rule_code = None
    rule_version = 1
    model = None

    def applies_to(self, subject):
        return isinstance(subject, self.model)

    def result(
        self,
        passed,
        *,
        affected_fields=(),
        evidence=None,
        message_code="",
        message_params=None,
    ):
        return RuleEvaluation(
            rule_code=self.rule_code,
            rule_version=self.rule_version,
            passed=passed,
            affected_fields=tuple(affected_fields),
            evidence=evidence or {},
            message_code=message_code,
            message_params=message_params or {},
        )
