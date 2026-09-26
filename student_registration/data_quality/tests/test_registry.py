import unittest

from student_registration.data_quality.registry import (
    DuplicateRuleRegistration,
    RuleRegistry,
)


class ExampleRule:
    rule_code = "DQ-EXAMPLE-001"
    rule_version = 1


class RuleRegistryTests(unittest.TestCase):
    def test_register_and_retrieve_rule(self):
        registry = RuleRegistry()
        evaluator = ExampleRule()

        self.assertIs(registry.register(evaluator), evaluator)
        self.assertIs(registry.get("DQ-EXAMPLE-001", 1), evaluator)
        self.assertEqual(registry.all(), (evaluator,))

    def test_duplicate_code_and_version_is_rejected(self):
        registry = RuleRegistry()
        registry.register(ExampleRule())

        with self.assertRaises(DuplicateRuleRegistration):
            registry.register(ExampleRule())

    def test_class_decorator_stores_an_instance_and_returns_the_class(self):
        registry = RuleRegistry()

        returned_class = registry.register(ExampleRule)

        self.assertIs(returned_class, ExampleRule)
        self.assertIsInstance(registry.get("DQ-EXAMPLE-001", 1), ExampleRule)
