import unittest
import os
import tempfile
from pathlib import Path

from scripts.spec_traceability_gate import (
    evaluate_changes,
    is_code_change,
    is_feature_spec_file,
    is_traceability_update,
)


class SpecTraceabilityGateTests(unittest.TestCase):
    VALID_SPEC_TEMPLATE = (
        "\n".join(
            [
                "## Spec Enrollment Checklist (Mandatory)",
                "- [x] Feature folder exists",
                "- [x] Spec created before implementation",
                "- [x] Goal, Acceptance Criteria, Test Mapping, and Traceability Matrix are complete before code changes",
                "## Goal",
                "## Acceptance Criteria",
                "## Test Mapping",
                "## Traceability Matrix",
            ]
        )
        + "\n"
    )

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

    def test_is_feature_spec_file_detects_expected_path(self):
        self.assertTrue(is_feature_spec_file(".specs/features/orders/spec.md"))

    def test_evaluate_changes_fails_when_code_without_traceability(self):
        result = evaluate_changes(["src/api/orders.py", "services/payments.ts"])
        self.assertFalse(result["passed"])
        self.assertGreaterEqual(len(result["violations"]), 1)

    def test_evaluate_changes_fails_when_no_feature_spec_update(self):
        result = evaluate_changes(
            [
                "src/api/orders.py",
                ".ai-docs/APP-BLUEPRINT.md",
            ]
        )
        self.assertFalse(result["passed"])
        self.assertTrue(
            any("feature spec updates" in issue for issue in result["violations"])
        )

    def test_evaluate_changes_passes_when_valid_feature_spec_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_cwd = Path.cwd()
            try:
                temp_path = Path(tmp)
                (temp_path / ".specs" / "features" / "orders").mkdir(parents=True)
                (temp_path / ".specs" / "features" / "orders" / "spec.md").write_text(
                    self.VALID_SPEC_TEMPLATE,
                    encoding="utf-8",
                )
                os.chdir(temp_path)

                result = evaluate_changes(
                    [
                        "src/api/orders.py",
                        ".specs/features/orders/spec.md",
                        ".ai-docs/APP-BLUEPRINT.md",
                    ]
                )
                self.assertTrue(result["passed"])
                self.assertEqual(result["violations"], [])
            finally:
                os.chdir(previous_cwd)

    def test_evaluate_changes_fails_when_feature_spec_missing_required_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_cwd = Path.cwd()
            try:
                temp_path = Path(tmp)
                (temp_path / ".specs" / "features" / "orders").mkdir(parents=True)
                (temp_path / ".specs" / "features" / "orders" / "spec.md").write_text(
                    "## Goal\nOnly goal\n",
                    encoding="utf-8",
                )
                os.chdir(temp_path)

                result = evaluate_changes(
                    [
                        "src/api/orders.py",
                        ".specs/features/orders/spec.md",
                    ]
                )
                self.assertFalse(result["passed"])
                self.assertTrue(
                    any(
                        "missing required section" in issue
                        for issue in result["violations"]
                    )
                )
            finally:
                os.chdir(previous_cwd)

    def test_strict_mode_fails_with_unchecked_checklist_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_cwd = Path.cwd()
            try:
                temp_path = Path(tmp)
                (temp_path / ".specs" / "features" / "orders").mkdir(parents=True)
                (temp_path / ".specs" / "features" / "orders" / "spec.md").write_text(
                    "\n".join(
                        [
                            "## Spec Enrollment Checklist (Mandatory)",
                            "- [ ] Feature folder exists",
                            "- [x] Spec created before implementation",
                            "## Goal",
                            "## Acceptance Criteria",
                            "## Test Mapping",
                            "## Traceability Matrix",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )
                os.chdir(temp_path)

                result = evaluate_changes(
                    [
                        "src/api/orders.py",
                        ".specs/features/orders/spec.md",
                    ],
                    strict_mode=True,
                )
                self.assertFalse(result["passed"])
                self.assertTrue(
                    any(
                        "checklist completion" in issue
                        for issue in result["violations"]
                    )
                )
            finally:
                os.chdir(previous_cwd)

    def test_strict_mode_fails_when_oversized_spec_not_normalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_cwd = Path.cwd()
            try:
                temp_path = Path(tmp)
                (temp_path / ".specs" / "features" / "orders").mkdir(parents=True)
                oversized = self.VALID_SPEC_TEMPLATE + ("line\n" * 20)
                (temp_path / ".specs" / "features" / "orders" / "spec.md").write_text(
                    oversized,
                    encoding="utf-8",
                )
                os.chdir(temp_path)

                result = evaluate_changes(
                    [
                        "src/api/orders.py",
                        ".specs/features/orders/spec.md",
                    ],
                    strict_mode=True,
                    max_spec_lines=10,
                )
                self.assertFalse(result["passed"])
                self.assertTrue(
                    any("spec is oversized" in issue for issue in result["violations"])
                )
            finally:
                os.chdir(previous_cwd)

    def test_strict_mode_passes_when_oversized_spec_is_normalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_cwd = Path.cwd()
            try:
                temp_path = Path(tmp)
                feature_dir = temp_path / ".specs" / "features" / "orders"
                (feature_dir / "spec").mkdir(parents=True)
                oversized = self.VALID_SPEC_TEMPLATE + ("line\n" * 20)
                (feature_dir / "spec.md").write_text(oversized, encoding="utf-8")
                (feature_dir / "spec" / "index.md").write_text(
                    "# Index\n", encoding="utf-8"
                )
                (feature_dir / "spec" / "acceptance-criteria.md").write_text(
                    "# Acceptance Criteria\n", encoding="utf-8"
                )
                (feature_dir / "spec" / "test-mapping.md").write_text(
                    "# Test Mapping\n", encoding="utf-8"
                )
                (feature_dir / "spec" / "traceability-matrix.md").write_text(
                    "# Traceability Matrix\n", encoding="utf-8"
                )
                os.chdir(temp_path)

                result = evaluate_changes(
                    [
                        "src/api/orders.py",
                        ".specs/features/orders/spec.md",
                    ],
                    strict_mode=True,
                    max_spec_lines=10,
                )
                self.assertTrue(result["passed"])
            finally:
                os.chdir(previous_cwd)


if __name__ == "__main__":
    unittest.main()
