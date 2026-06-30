import importlib.machinery
import importlib.util
import tempfile
import unittest
from pathlib import Path


def load_bootstrap_module():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "ai-docs-bootstrap"
    loader = importlib.machinery.SourceFileLoader("ai_docs_bootstrap", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError(f"Unable to build module spec for {script_path}")

    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


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

            specs_index = (project_dir / ".specs" / "memory.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("payments: .specs/features/payments/spec.md", specs_index)
            self.assertIn("orders: .specs/features/orders/spec.md", specs_index)
            self.assertIn("billing: .specs/features/billing/spec.md", specs_index)


if __name__ == "__main__":
    unittest.main()
