import unittest
import tempfile
from pathlib import Path

from src.generators.compliance import (
    apply_level_3_patch_proposals,
    generate_ai_assisted_compliance_analysis,
    generate_compliance_dashboard_html,
    generate_level_2_compliance_scanning,
    generate_level_3_applied_patch_report,
    generate_level_3_compliance_patterns,
    generate_level_3_pattern_injection_report,
    generate_level_3_patch_proposals,
)


class ComplianceGeneratorTests(unittest.TestCase):
    def test_level_2_generates_only_requested_frameworks(self):
        packs = [
            {"key": "pci-dss", "name": "PCI DSS"},
            {"key": "gdpr", "name": "GDPR"},
        ]

        files = generate_level_2_compliance_scanning(packs)

        self.assertIn(".specs/compliance/pci-dss-scanning.md", files)
        self.assertIn(".specs/compliance/gdpr-scanning.md", files)
        self.assertNotIn(".specs/compliance/hipaa-scanning.md", files)

    def test_level_2_hipaa_contains_phi_detection_pattern(self):
        packs = [{"key": "hipaa", "name": "HIPAA"}]

        files = generate_level_2_compliance_scanning(packs)
        hipaa_doc = files[".specs/compliance/hipaa-scanning.md"]

        self.assertIn("HIPAA: Scanning & Validation (Level 2)", hipaa_doc)
        self.assertIn('grep -r "\\\\d{{3}}-\\\\d{{2}}-\\\\d{{4}}"', hipaa_doc)

    def test_level_3_generates_all_pattern_files_when_all_packs_selected(self):
        packs = [
            {"key": "pci-dss", "name": "PCI DSS"},
            {"key": "hipaa", "name": "HIPAA"},
            {"key": "gdpr", "name": "GDPR"},
            {"key": "soc2", "name": "SOC 2"},
            {"key": "ccpa", "name": "CCPA/CPRA"},
            {"key": "iso27001", "name": "ISO 27001"},
        ]

        files = generate_level_3_compliance_patterns(packs)

        expected = {
            ".specs/compliance/pci-dss-patterns.md",
            ".specs/compliance/hipaa-patterns.md",
            ".specs/compliance/gdpr-patterns.md",
            ".specs/compliance/soc2-patterns.md",
            ".specs/compliance/ccpa-patterns.md",
            ".specs/compliance/iso27001-patterns.md",
        }
        self.assertTrue(expected.issubset(set(files.keys())))

    def test_level_3_pci_contains_core_examples(self):
        packs = [{"key": "pci-dss", "name": "PCI DSS"}]

        files = generate_level_3_compliance_patterns(packs)
        pci_doc = files[".specs/compliance/pci-dss-patterns.md"]

        self.assertIn("Tokenize Card Data at Ingress", pci_doc)
        self.assertIn("Python (FastAPI)", pci_doc)
        self.assertIn("Node.js (Express)", pci_doc)
        self.assertIn("Go (net/http)", pci_doc)

    def test_level_3_empty_input_returns_empty_mapping(self):
        files = generate_level_3_compliance_patterns([])
        self.assertEqual(files, {})

    def test_level_2_all_framework_scanning_files_generated(self):
        packs = [
            {"key": "pci-dss", "name": "PCI DSS"},
            {"key": "hipaa", "name": "HIPAA"},
            {"key": "gdpr", "name": "GDPR"},
            {"key": "soc2", "name": "SOC 2"},
            {"key": "ccpa", "name": "CCPA/CPRA"},
            {"key": "iso27001", "name": "ISO 27001"},
        ]

        files = generate_level_2_compliance_scanning(packs)
        expected = {
            ".specs/compliance/pci-dss-scanning.md",
            ".specs/compliance/hipaa-scanning.md",
            ".specs/compliance/gdpr-scanning.md",
            ".specs/compliance/soc2-scanning.md",
            ".specs/compliance/ccpa-scanning.md",
            ".specs/compliance/iso27001-scanning.md",
        }

        self.assertTrue(expected.issubset(set(files.keys())))

    def test_pci_scanning_contains_required_checklist_items(self):
        files = generate_level_2_compliance_scanning(
            [{"key": "pci-dss", "name": "PCI DSS"}]
        )
        pci_doc = files[".specs/compliance/pci-dss-scanning.md"]

        self.assertIn("TLS 1.2+ enforced", pci_doc)
        self.assertIn("HSTS headers set", pci_doc)
        self.assertIn(
            "Session cookies marked Secure + HttpOnly + SameSite=Strict", pci_doc
        )

    def test_scanning_docs_include_remediation_guidance(self):
        files = generate_level_2_compliance_scanning(
            [
                {"key": "pci-dss", "name": "PCI DSS"},
                {"key": "hipaa", "name": "HIPAA"},
                {"key": "gdpr", "name": "GDPR"},
            ]
        )

        self.assertIn(
            "## Remediation Path", files[".specs/compliance/pci-dss-scanning.md"]
        )
        self.assertIn(
            "## Remediation Path", files[".specs/compliance/hipaa-scanning.md"]
        )
        self.assertIn(
            "## Remediation Path", files[".specs/compliance/gdpr-scanning.md"]
        )

    def test_level_2_spanish_localizes_headings(self):
        files = generate_level_2_compliance_scanning(
            [{"key": "gdpr", "name": "GDPR"}],
            locale="es",
        )
        gdpr_doc = files[".specs/compliance/gdpr-scanning.md"]

        self.assertIn("## Reglas de Escaneo de Codigo", gdpr_doc)
        self.assertIn("## Ruta de Remediacion", gdpr_doc)

    def test_level_3_french_localizes_heading(self):
        files = generate_level_3_compliance_patterns(
            [{"key": "hipaa", "name": "HIPAA"}],
            locale="fr",
        )
        hipaa_doc = files[".specs/compliance/hipaa-patterns.md"]

        self.assertIn("HIPAA: Modeles et Exemples d Implementation", hipaa_doc)

    def test_level_2_includes_regional_variant_section(self):
        files = generate_level_2_compliance_scanning(
            [{"key": "soc2", "name": "SOC 2"}],
            locale="en",
            compliance_region="eu",
        )
        soc2_doc = files[".specs/compliance/soc2-scanning.md"]

        self.assertIn("## Regional Variant", soc2_doc)
        self.assertIn("- Region: EU", soc2_doc)
        self.assertIn("EU regional guidance", soc2_doc)

    def test_level_3_pattern_injection_report_detects_weak_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "src").mkdir(parents=True, exist_ok=True)
            (project_dir / "src" / "payments.py").write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )

            report = generate_level_3_pattern_injection_report(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
            )

            self.assertIsNotNone(report)
            self.assertIn("pci-weak-hash", report)
            self.assertIn("src/payments.py", report)

    def test_level_3_pattern_injection_report_returns_none_when_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "src").mkdir(parents=True, exist_ok=True)
            (project_dir / "src" / "safe.py").write_text(
                "def ok(x):\n    return x\n",
                encoding="utf-8",
            )

            report = generate_level_3_pattern_injection_report(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
            )

            self.assertIsNone(report)

    def test_level_3_patch_proposals_include_diff_for_weak_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "src").mkdir(parents=True, exist_ok=True)
            (project_dir / "src" / "hashing.py").write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )

            proposals = generate_level_3_patch_proposals(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
            )

            self.assertIsNotNone(proposals)
            self.assertIn("LEVEL 3 Auto-Patch".lower(), proposals.lower())
            self.assertIn("src/hashing.py", proposals)
            self.assertIn("-     return md5(v.encode()).hexdigest()", proposals)
            self.assertIn("+     return sha256(v.encode()).hexdigest()", proposals)

    def test_level_3_patch_proposals_returns_none_without_mappable_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "src").mkdir(parents=True, exist_ok=True)
            (project_dir / "src" / "safe.py").write_text(
                "def ok(v):\n    return v\n",
                encoding="utf-8",
            )

            proposals = generate_level_3_patch_proposals(
                project_dir,
                [{"key": "hipaa", "name": "HIPAA"}],
            )

            self.assertIsNone(proposals)

    def test_apply_level_3_patch_proposals_updates_file_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            target = project_dir / "src" / "hashing.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )

            result = apply_level_3_patch_proposals(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
            )

            self.assertEqual(len(result["applied"]), 1)
            updated = target.read_text(encoding="utf-8")
            self.assertIn("sha256(v.encode()).hexdigest()", updated)

    def test_apply_level_3_patch_proposals_respects_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            src_target = project_dir / "src" / "hashing.py"
            test_target = project_dir / "tests" / "hashing.py"
            src_target.parent.mkdir(parents=True, exist_ok=True)
            test_target.parent.mkdir(parents=True, exist_ok=True)
            src_target.write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )
            test_target.write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )

            result = apply_level_3_patch_proposals(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
                patch_allowlist=["src"],
                patch_denylist=[],
            )

            self.assertEqual(len(result["applied"]), 1)
            self.assertIn("sha256", src_target.read_text(encoding="utf-8"))
            self.assertIn("md5", test_target.read_text(encoding="utf-8"))

    def test_apply_level_3_patch_proposals_respects_denylist(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            blocked_target = project_dir / "src" / "legacy" / "hashing.py"
            blocked_target.parent.mkdir(parents=True, exist_ok=True)
            blocked_target.write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )

            result = apply_level_3_patch_proposals(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
                patch_allowlist=["src"],
                patch_denylist=["src/legacy"],
            )

            self.assertEqual(len(result["applied"]), 0)
            self.assertIn("md5", blocked_target.read_text(encoding="utf-8"))

    def test_generate_level_3_applied_patch_report_contains_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            p = project_dir / "src" / "hashing.py"
            p.parent.mkdir(parents=True, exist_ok=True)
            report = generate_level_3_applied_patch_report(
                project_dir,
                [
                    {
                        "framework": "pci-dss",
                        "rule_id": "pci-weak-hash",
                        "path": p,
                        "line_no": 2,
                        "before": "    return md5(v.encode()).hexdigest()",
                        "after": "    return sha256(v.encode()).hexdigest()",
                    }
                ],
            )

            self.assertIsNotNone(report)
            self.assertIn("Level 3 Auto-Patch Results", report)
            self.assertIn("src/hashing.py:2", report)

    def test_ai_assisted_compliance_analysis_includes_risk_and_recommendations(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            target = project_dir / "src" / "billing.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )

            analysis = generate_ai_assisted_compliance_analysis(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
            )

            self.assertIsNotNone(analysis)
            self.assertIn("AI-Assisted Compliance Analysis", analysis)
            self.assertIn("Aggregate risk score:", analysis)
            self.assertIn("Recommended Architecture Changes", analysis)
            self.assertIn("PCI-DSS", analysis)

    def test_ai_assisted_compliance_analysis_returns_none_without_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            target = project_dir / "src" / "safe.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("def ok(v):\n    return v\n", encoding="utf-8")

            analysis = generate_ai_assisted_compliance_analysis(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
            )

            self.assertIsNone(analysis)

    def test_compliance_dashboard_html_contains_status_and_progress_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "src").mkdir(parents=True, exist_ok=True)
            (project_dir / "src" / "billing.py").write_text(
                "def digest(v):\n    return md5(v.encode()).hexdigest()\n",
                encoding="utf-8",
            )
            (project_dir / ".specs" / "compliance").mkdir(parents=True, exist_ok=True)
            (project_dir / ".specs" / "compliance" / "pci-dss-scanning.md").write_text(
                "# stub\n",
                encoding="utf-8",
            )

            dashboard = generate_compliance_dashboard_html(
                project_dir,
                [{"key": "pci-dss", "name": "PCI DSS"}],
                planned_output_paths=[
                    ".specs/compliance/pci-dss-scanning.md",
                    ".specs/compliance/pci-dss-patterns.md",
                ],
            )

            self.assertIn("Compliance Dashboard", dashboard)
            self.assertIn("File Generation Progress", dashboard)
            self.assertIn("Real-Time Scanning Results", dashboard)
            self.assertIn("pci-weak-hash", dashboard)

    def test_compliance_dashboard_html_handles_empty_frameworks(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            dashboard = generate_compliance_dashboard_html(
                project_dir,
                [],
                planned_output_paths=[],
            )

            self.assertIn("No compliance frameworks selected.", dashboard)


if __name__ == "__main__":
    unittest.main()
