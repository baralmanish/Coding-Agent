import unittest

from scripts.spec_traceability_gate import (
    evaluate_changes,
    is_code_change,
    is_traceability_update,
)


class SpecTraceabilityGateTests(unittest.TestCase):
    def test_is_code_change_for_src_python(self):
        self.assertTrue(is_code_change("src/service/payments.py"))

    def test_is_code_change_for_root_language_file(self):
        self.assertTrue(is_code_change("main.ts"))

    def test_is_code_change_excludes_specs(self):
        self.assertFalse(is_code_change(".specs/features/payments/spec.md"))

    def test_is_traceability_update_for_specs(self):
        self.assertTrue(is_traceability_update(".specs/features/orders/spec.md"))

    def test_is_traceability_update_for_ai_docs(self):
        self.assertTrue(is_traceability_update(".ai-docs/APP-BLUEPRINT.md"))

    def test_is_traceability_update_for_core_guides(self):
        self.assertTrue(is_traceability_update("AGENTS.md"))

    def test_evaluate_changes_fails_when_code_without_traceability(self):
        result = evaluate_changes(["src/api/orders.py", "services/payments.ts"])
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["violations"]), 1)

    def test_evaluate_changes_passes_when_traceability_present(self):
        result = evaluate_changes(
            [
                "src/api/orders.py",
                ".specs/features/orders/spec.md",
                ".ai-docs/APP-BLUEPRINT.md",
            ]
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["violations"], [])


if __name__ == "__main__":
    unittest.main()
