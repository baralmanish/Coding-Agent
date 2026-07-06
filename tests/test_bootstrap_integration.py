import json
import tempfile
import time
import unittest
from pathlib import Path
from tests.helpers import load_bootstrap_module


mod = load_bootstrap_module()


class BootstrapIntegrationTests(unittest.TestCase):
    def _build_ctx(
        self,
        project_dir: Path,
        target_os: str,
        compliance_keys: list[str],
        compliance_level: int,
    ) -> dict:
        stack = mod.detect_stack(project_dir)
        app_intent = "general-app"
        _, _, app_blueprint = mod.resolve_app_blueprint(
            app_intent,
            {
                "frameworks": stack.get("frameworks", []),
                "languages": stack.get("languages", []),
            },
        )
        compliance_packs = mod.resolve_compliance_packs(app_intent, compliance_keys)
        package_guidance = mod.resolve_package_guidance(stack)
        return {
            "generated_at": "2026-06-30 12:00:00 UTC",
            "project_type": "new",
            "target_os": target_os,
            "locale": "en",
            "compliance_region": "",
            "stack": stack,
            "app_intent": app_intent,
            "app_intent_input": app_intent,
            "app_blueprint": app_blueprint,
            "compliance_packs": compliance_packs,
            "compliance_level": compliance_level,
            "package_guidance": package_guidance,
            "agents": list(mod.DEFAULT_AGENTS),
        }

    def test_level_2_compliance_combination_generates_scanning_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            ctx = self._build_ctx(
                project_dir,
                target_os="macos",
                compliance_keys=["pci-dss", "hipaa", "gdpr"],
                compliance_level=2,
            )

            generated, _ = mod.generate_files(
                project_dir, ctx, markdown_context=[], check_mode=False
            )
            generated_set = set(generated)

            self.assertIn(".specs/compliance/pci-dss-scanning.md", generated_set)
            self.assertIn(".specs/compliance/hipaa-scanning.md", generated_set)
            self.assertIn(".specs/compliance/gdpr-scanning.md", generated_set)
            self.assertNotIn(".specs/compliance/pci-dss-patterns.md", generated_set)

    def test_target_os_is_reflected_in_generated_context_snapshot(self):
        for os_name in ["macos", "windows"]:
            with tempfile.TemporaryDirectory() as tmp:
                project_dir = Path(tmp)
                ctx = self._build_ctx(
                    project_dir,
                    target_os=os_name,
                    compliance_keys=[],
                    compliance_level=1,
                )

                mod.generate_files(
                    project_dir, ctx, markdown_context=[], check_mode=False
                )
                snapshot = (project_dir / ".ai-docs" / "CONTEXT-SNAPSHOT.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(f"- **Target OS**: {os_name}", snapshot)

    def test_feature_specs_generated_from_source_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "src" / "payments").mkdir(parents=True, exist_ok=True)
            (project_dir / "src" / "orders").mkdir(parents=True, exist_ok=True)
            (project_dir / "src" / "billing.py").write_text(
                "print('ok')\n", encoding="utf-8"
            )

            ctx = self._build_ctx(
                project_dir,
                target_os="linux",
                compliance_keys=[],
                compliance_level=1,
            )

            generated, _ = mod.generate_files(
                project_dir, ctx, markdown_context=[], check_mode=False
            )
            generated_set = set(generated)

            self.assertIn(".specs/features/payments/spec.md", generated_set)
            self.assertIn(".specs/features/orders/spec.md", generated_set)
            self.assertIn(".specs/features/billing/spec.md", generated_set)

            payments_spec = (
                project_dir / ".specs" / "features" / "payments" / "spec.md"
            ).read_text(encoding="utf-8")
            self.assertIn("## Spec Enrollment Checklist (Mandatory)", payments_spec)
            self.assertIn("## Traceability Matrix", payments_spec)
            self.assertIn("## Spec Normalization (When Spec Gets Large)", payments_spec)

            specs_index = (project_dir / ".specs" / "memory.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("payments: .specs/features/payments/spec.md", specs_index)
            self.assertIn("orders: .specs/features/orders/spec.md", specs_index)
            self.assertIn("billing: .specs/features/billing/spec.md", specs_index)

    def test_feature_specs_localize_when_locale_is_spanish(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "src" / "analytics").mkdir(parents=True, exist_ok=True)

            ctx = self._build_ctx(
                project_dir,
                target_os="linux",
                compliance_keys=[],
                compliance_level=1,
            )
            ctx["locale"] = "es"

            mod.generate_files(project_dir, ctx, markdown_context=[], check_mode=False)

            spec_doc = (
                project_dir / ".specs" / "features" / "analytics" / "spec.md"
            ).read_text(encoding="utf-8")
            self.assertIn("# Especificacion de Funcionalidad: analytics", spec_doc)

    def test_containerization_docs_generated_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            ctx = self._build_ctx(
                project_dir,
                target_os="linux",
                compliance_keys=[],
                compliance_level=1,
            )

            generated, _ = mod.generate_files(
                project_dir, ctx, markdown_context=[], check_mode=False
            )
            generated_set = set(generated)

            self.assertIn(".ai-docs/CONTAINERIZATION.md", generated_set)
            container_doc = (
                project_dir / ".ai-docs" / "CONTAINERIZATION.md"
            ).read_text(encoding="utf-8")
            self.assertIn("# Containerization Baseline", container_doc)
            self.assertIn("## Dockerfile Baseline", container_doc)
            self.assertIn("## Kubernetes Baseline", container_doc)

    def test_custom_agent_support_generates_custom_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            stack = mod.detect_stack(project_dir)

            new_details = {
                "target_os": "macos",
                "app_intent": "general-app",
                "app_intent_input": "general-app",
                "compliance_keys": [],
                "compliance_level": 1,
                "agents": list(mod.DEFAULT_AGENTS),
                "custom_frameworks": ["GraphQL Mesh"],
                "custom_compliance_rules": [
                    {
                        "key": "internal-sec",
                        "name": "Internal Security",
                        "checks": ["Enforce tenant encryption"],
                    }
                ],
                "custom_feature_templates": [
                    {
                        "name": "risk-engine",
                        "template": "# Feature Spec: Risk Engine\n\n## Goal\nCustom risk workflow",
                    }
                ],
            }

            ctx = mod.build_common_context(
                "new",
                stack,
                new_details,
                "2026-06-30 12:00:00 UTC",
            )

            generated, _ = mod.generate_files(
                project_dir, ctx, markdown_context=[], check_mode=False
            )
            generated_set = set(generated)

            self.assertIn("GraphQL Mesh", ctx["stack"]["frameworks"])
            compliance_keys = [item.get("key") for item in ctx["compliance_packs"]]
            self.assertIn("internal-sec", compliance_keys)
            self.assertIn(".specs/features/risk-engine/spec.md", generated_set)
            self.assertIn(".ai-docs/CUSTOM-AGENT-CONFIG.md", generated_set)

            custom_spec = (
                project_dir / ".specs" / "features" / "risk-engine" / "spec.md"
            ).read_text(encoding="utf-8")
            self.assertIn("Custom risk workflow", custom_spec)

    def test_run_metrics_and_json_report_helpers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            start = time.perf_counter() - 0.01
            metrics = mod.build_run_metrics(
                project_dir=project_dir,
                mode="existing",
                check_mode=False,
                dry_run=True,
                generated_files=[".specs/compliance/pci-dss-scanning.md", "AGENTS.md"],
                changed_files=["AGENTS.md"],
                start_time=start,
                ctx={
                    "feature_metrics": {
                        "outputs": {
                            "base-docs": ["AGENTS.md"],
                            "compliance-level-2": [
                                ".specs/compliance/pci-dss-scanning.md"
                            ],
                        },
                        "durations_ms": {
                            "base-docs": 4,
                            "compliance-level-2": 9,
                        },
                    }
                },
            )

            self.assertEqual(metrics["mode"], "existing")
            self.assertTrue(metrics["dry_run"])
            self.assertEqual(metrics["compliance_files"], 1)
            self.assertGreaterEqual(metrics["duration_ms"], 0)
            self.assertEqual(
                metrics["feature_metrics"]["base-docs"]["generated_files"], 1
            )
            self.assertEqual(
                metrics["feature_metrics"]["base-docs"]["changed_files"], 1
            )
            self.assertEqual(
                metrics["feature_metrics"]["compliance-level-2"]["duration_ms"], 9
            )

            report_path = project_dir / "reports" / "run.json"
            mod.write_json_report(report_path, metrics)
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["mode"], "existing")
            self.assertIn("feature_metrics", written)

    def test_update_performance_history_detects_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            history_path = project_dir / "benchmarks" / "performance-history.json"

            base = {
                "timestamp": "2026-06-30 12:00:00 UTC",
                "mode": "existing",
                "changed_files": 1,
                "feature_metrics": {
                    "base-docs": {"generated_files": 2, "duration_ms": 15},
                    "compliance-level-2": {"generated_files": 1, "duration_ms": 30},
                },
            }
            mod.update_performance_history(history_path, {**base, "duration_ms": 100})
            mod.update_performance_history(history_path, {**base, "duration_ms": 110})
            result = mod.update_performance_history(
                history_path, {**base, "duration_ms": 220}
            )

            self.assertTrue(result["regression"])
            self.assertGreater(
                result["current_duration_ms"], result["baseline_duration_ms"]
            )
            self.assertEqual(
                result["slowest_features"][0]["feature"], "compliance-level-2"
            )

    def test_feature_toggle_disables_compliance_dashboard_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            ctx = self._build_ctx(
                project_dir,
                target_os="linux",
                compliance_keys=["pci-dss"],
                compliance_level=3,
            )
            ctx["active_features"] = [
                "base-docs",
                "agent-docs",
                "feature-specs",
                "compliance-level-2",
                "compliance-level-3",
                "patch-proposals",
                "ai-analysis",
            ]

            generated, _ = mod.generate_files(
                project_dir, ctx, markdown_context=[], check_mode=False
            )
            generated_set = set(generated)
            self.assertNotIn(".specs/compliance/dashboard/index.html", generated_set)

    def test_feature_status_file_lists_active_features(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            ctx = self._build_ctx(
                project_dir,
                target_os="linux",
                compliance_keys=[],
                compliance_level=1,
            )
            ctx["active_features"] = ["base-docs", "feature-catalog"]

            mod.generate_files(project_dir, ctx, markdown_context=[], check_mode=False)
            feature_doc = (project_dir / ".ai-docs" / "FEATURES.md").read_text(
                encoding="utf-8"
            )

            self.assertIn("feature-catalog", ctx["feature_metrics"]["outputs"])
            self.assertIn("Selected Profile", feature_doc)
            self.assertIn("custom", feature_doc)
            self.assertIn("Available Features", feature_doc)
            self.assertIn("Active Features For This Run", feature_doc)
            self.assertIn("- feature-catalog", feature_doc)

    def test_resolve_active_features_rejects_unknown_feature(self):
        with self.assertRaises(ValueError):
            mod.resolve_active_features(
                feature_profile=None,
                explicit_features=["base-docs", "not-real"],
                enable_features=[],
                disable_features=[],
                apply_auto_patches=False,
            )

    def test_resolve_active_features_can_incrementally_add_features(self):
        active = mod.resolve_active_features(
            feature_profile=None,
            explicit_features=["base-docs", "compliance-level-3"],
            enable_features=["feature-catalog", "compliance-dashboard"],
            disable_features=[],
            apply_auto_patches=False,
        )

        self.assertIn("base-docs", active)
        self.assertIn("feature-catalog", active)
        self.assertIn("compliance-dashboard", active)

    def test_resolve_active_features_can_disable_feature_specs(self):
        active = mod.resolve_active_features(
            feature_profile="standard",
            explicit_features=[],
            enable_features=[],
            disable_features=["feature-specs"],
            apply_auto_patches=False,
        )

        self.assertNotIn("feature-specs", active)

    def test_resolve_active_features_rejects_missing_dependency(self):
        with self.assertRaisesRegex(ValueError, "compliance-level-3"):
            mod.resolve_active_features(
                feature_profile=None,
                explicit_features=["base-docs", "compliance-dashboard"],
                enable_features=[],
                disable_features=[],
                apply_auto_patches=False,
            )

    def test_resolve_active_features_rejects_auto_patch_without_flag(self):
        with self.assertRaisesRegex(ValueError, "--apply-auto-patches"):
            mod.resolve_active_features(
                feature_profile=None,
                explicit_features=[
                    "base-docs",
                    "compliance-level-3",
                    "auto-patch-apply",
                ],
                enable_features=[],
                disable_features=[],
                apply_auto_patches=False,
            )

    def test_resolve_active_features_accepts_profile_with_overrides(self):
        active = mod.resolve_active_features(
            feature_profile="standard",
            explicit_features=[],
            enable_features=["compliance-level-3", "compliance-dashboard"],
            disable_features=["custom-agent-config"],
            apply_auto_patches=False,
        )

        self.assertIn("base-docs", active)
        self.assertIn("feature-catalog", active)
        self.assertIn("compliance-level-3", active)
        self.assertIn("compliance-dashboard", active)
        self.assertNotIn("custom-agent-config", active)

    def test_resolve_active_features_rejects_profile_with_explicit_features(self):
        with self.assertRaisesRegex(ValueError, "--feature-profile"):
            mod.resolve_active_features(
                feature_profile="minimal",
                explicit_features=["base-docs"],
                enable_features=[],
                disable_features=[],
                apply_auto_patches=False,
            )

    def test_resolve_feature_profile_rejects_unknown_profile(self):
        with self.assertRaisesRegex(ValueError, "Unsupported feature profile"):
            mod.resolve_feature_profile("not-real")

    def test_load_feature_config_rejects_unknown_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "features.json"
            config_path.write_text(
                json.dumps(
                    {
                        "feature_profile": "standard",
                        "unknown_key": True,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError, r"Unknown key\(s\) in --features-config"
            ):
                mod.load_feature_config(str(config_path))

    def test_write_feature_config_exports_resolved_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "feature-config.json"
            written_path = mod.write_feature_config(
                path_value=str(output_path),
                selected_feature_profile="standard",
                active_features=["base-docs", "feature-catalog"],
                enable_features=["feature-catalog"],
                disable_features=["compliance-dashboard"],
                apply_auto_patches=False,
            )

            self.assertEqual(written_path, output_path)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["feature_profile"], "standard")
            self.assertEqual(payload["features"], ["base-docs", "feature-catalog"])
            self.assertEqual(payload["enable_features"], ["feature-catalog"])
            self.assertEqual(payload["disable_features"], ["compliance-dashboard"])
            self.assertFalse(payload["apply_auto_patches"])

    def test_resolve_active_features_accepts_renamed_alias(self):
        active = mod.resolve_active_features(
            feature_profile=None,
            explicit_features=[
                "base-docs",
                "compliance-level-3",
                "ai-compliance-analysis",
            ],
            enable_features=[],
            disable_features=[],
            apply_auto_patches=False,
        )

        self.assertIn("ai-analysis", active)
        self.assertNotIn("ai-compliance-analysis", active)

    def test_resolve_active_features_rejects_removed_feature_with_migration(self):
        with self.assertRaisesRegex(ValueError, "has been removed"):
            mod.resolve_active_features(
                feature_profile=None,
                explicit_features=["base-docs", "compliance-report"],
                enable_features=[],
                disable_features=[],
                apply_auto_patches=False,
            )

    def test_feature_status_md_includes_lifecycle_labels(self):
        content = mod.generate_feature_status_md(
            active_features=["base-docs", "ai-analysis"],
            selected_profile="custom",
        )
        self.assertIn("base-docs [stable]", content)
        self.assertIn("ai-analysis [experimental]", content)


if __name__ == "__main__":
    unittest.main()
