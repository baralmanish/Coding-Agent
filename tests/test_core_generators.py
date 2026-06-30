import unittest

from src.generators.core import (
    generate_agent_specific_docs,
    generate_agents_md,
    generate_app_blueprint_md,
    generate_context_snapshot,
    generate_index_md,
)


class CoreGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.ctx = {
            "generated_at": "2026-06-30 12:00:00 UTC",
            "project_type": "existing",
            "target_os": "macos",
            "app_intent": "general-app",
            "app_intent_input": "general-app",
            "agents": ["cursor", "github-copilot"],
            "stack": {
                "languages": ["Python"],
                "frameworks": ["FastAPI"],
                "package_managers": ["pip"],
                "packages": ["fastapi", "pydantic"],
                "scripts": {"test": ["pytest"]},
            },
            "app_blueprint": {
                "label": "General App",
                "description": "Baseline delivery profile",
                "capabilities": ["Auth", "Observability"],
                "suggestions": ["Add CI checks"],
                "intent_ranking": [
                    {
                        "label": "General App",
                        "score": 3,
                        "base_score": 2,
                        "framework_bonus": 1,
                        "matched_keywords": ["api"],
                    }
                ],
            },
            "compliance_level": 2,
            "compliance_packs": [
                {"key": "soc2", "name": "SOC 2", "checks": ["Audit access"]}
            ],
            "package_guidance": {
                "recommended_packages": ["httpx"],
                "avoid_packages": ["legacy-lib"],
                "audit_commands": ["pip-audit"],
            },
        }

    def test_generate_agents_md_contains_core_context(self):
        doc = generate_agents_md(self.ctx)
        self.assertIn("# AGENTS.md", doc)
        self.assertIn("Project type: existing", doc)
        self.assertIn("Target OS: macos", doc)
        self.assertIn("Languages: Python", doc)

    def test_generate_app_blueprint_md_includes_compliance_and_guidance(self):
        doc = generate_app_blueprint_md(self.ctx)
        self.assertIn("# Application Blueprint", doc)
        self.assertIn("SOC 2 (soc2)", doc)
        self.assertIn("- httpx", doc)
        self.assertIn("- legacy-lib", doc)
        self.assertIn("`pip-audit`", doc)

    def test_generate_index_md_sorts_files(self):
        files = ["b.md", "a.md", "c.md"]
        index_doc = generate_index_md(self.ctx, files)
        self.assertLess(index_doc.find("- a.md"), index_doc.find("- b.md"))
        self.assertLess(index_doc.find("- b.md"), index_doc.find("- c.md"))

    def test_generate_context_snapshot_mentions_detected_values(self):
        markdown_context = [{"path": "README.md", "preview": "Project intro"}]
        snapshot = generate_context_snapshot(self.ctx, markdown_context)
        self.assertIn("# Context Snapshot", snapshot)
        self.assertIn("FastAPI", snapshot)
        self.assertIn("soc2", snapshot)
        self.assertIn("README.md", snapshot)

    def test_generate_agent_specific_docs_returns_required_files(self):
        docs = generate_agent_specific_docs(self.ctx)
        self.assertIn(".cursor/rules/project.mdc", docs)
        self.assertIn(".github/copilot-instructions.md", docs)
        self.assertIn("Cursor Configuration", docs[".cursor/rules/project.mdc"])


if __name__ == "__main__":
    unittest.main()
