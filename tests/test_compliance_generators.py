import unittest

from src.generators.compliance import (
    generate_level_2_compliance_scanning,
    generate_level_3_compliance_patterns,
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


if __name__ == "__main__":
    unittest.main()
