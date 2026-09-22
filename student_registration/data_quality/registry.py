class DuplicateRuleRegistration(ValueError):
    """Raised when the same rule code and version is registered twice."""


class RuleRegistry:
    """In-process registry for deterministic rule evaluator callables."""

    def __init__(self):
        self._evaluators = {}

    def register(self, evaluator):
        key = (evaluator.rule_code, evaluator.rule_version)
        if key in self._evaluators:
            raise DuplicateRuleRegistration(
                f"Rule {evaluator.rule_code} v{evaluator.rule_version} is already registered"
            )
        self._evaluators[key] = evaluator
        return evaluator

    def get(self, rule_code, rule_version=1):
        return self._evaluators[(rule_code, rule_version)]

    def all(self):
        return tuple(self._evaluators.values())


registry = RuleRegistry()
