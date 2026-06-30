import json
import tempfile
import unittest
from pathlib import Path

from src.utils.file_io import (
    append_changelog,
    ensure_dir,
    gather_existing_markdown_context,
    load_previous_metadata,
    normalize_text,
    read_json_file,
    read_text_if_exists,
    write_metadata,
    write_text,
)


class FileIOUtilsTests(unittest.TestCase):
    def test_ensure_dir_and_write_text_create_nested_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            nested_file = base / "a" / "b" / "c.txt"
            write_text(nested_file, "hello")
            self.assertTrue(nested_file.exists())
            self.assertEqual(nested_file.read_text(encoding="utf-8"), "hello\n")

    def test_read_text_if_exists_and_normalize_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            missing = base / "missing.txt"
            self.assertEqual(read_text_if_exists(missing), "")
            self.assertEqual(normalize_text("line\n\n"), "line\n")

    def test_append_changelog_uses_injected_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            changelog = base / ".ai-docs" / "CHANGELOG.md"
            append_changelog(
                changelog,
                "Generated files",
                now_utc_fn=lambda: "2026-06-30 12:00:00 UTC",
            )
            content = changelog.read_text(encoding="utf-8")
            self.assertIn("# AI Docs Changelog", content)
            self.assertIn("## 2026-06-30 12:00:00 UTC", content)
            self.assertIn("- Generated files", content)

    def test_load_previous_metadata_and_write_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            payload = {"generator_version": "1.0.0", "generated_files": ["AGENTS.md"]}
            write_metadata(project, payload)
            loaded = load_previous_metadata(project)
            self.assertEqual(loaded["generator_version"], "1.0.0")
            self.assertEqual(loaded["generated_files"], ["AGENTS.md"])

    def test_read_json_file_handles_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            valid = base / "good.json"
            invalid = base / "bad.json"
            valid.write_text(json.dumps({"ok": True}), encoding="utf-8")
            invalid.write_text("{bad json", encoding="utf-8")

            self.assertEqual(read_json_file(valid), {"ok": True})
            self.assertEqual(read_json_file(invalid), {})
            self.assertEqual(read_json_file(base / "missing.json"), {})

    def test_gather_existing_markdown_context_filters_generated_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            ensure_dir(project / ".ai-docs")
            ensure_dir(project / ".github")
            ensure_dir(project / "docs")
            (project / "README.md").write_text("repo readme", encoding="utf-8")
            (project / "AGENTS.md").write_text("generated", encoding="utf-8")
            (project / ".ai-docs" / "NOTES.md").write_text("internal", encoding="utf-8")
            (project / ".github" / "guide.md").write_text("config", encoding="utf-8")
            (project / "docs" / "feature.md").write_text(
                "feature details", encoding="utf-8"
            )

            docs = gather_existing_markdown_context(project, max_files=10)
            paths = {d["path"] for d in docs}

            self.assertIn("README.md", paths)
            self.assertIn("docs/feature.md", paths)
            self.assertNotIn("AGENTS.md", paths)
            self.assertNotIn(".ai-docs/NOTES.md", paths)
            self.assertNotIn(".github/guide.md", paths)


if __name__ == "__main__":
    unittest.main()
