"""File I/O utilities for reading and writing project files."""

from pathlib import Path
from typing import Any
import json


def ensure_dir(path: Path) -> None:
    """Create directory and all parent directories if needed."""
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    """Write text content to a file with trailing newline."""
    ensure_dir(path.parent)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_text_if_exists(path: Path) -> str:
    """Read text from a file, returning empty string if file doesn't exist."""
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def normalize_text(content: str) -> str:
    """Normalize text by removing trailing whitespace and adding single newline."""
    return content.rstrip() + "\n"


def append_changelog(changelog_path: Path, summary: str, now_utc_fn=None) -> None:
    """Append an entry to the changelog file.

    Args:
        changelog_path: Path to the changelog file
        summary: Summary text for the changelog entry
        now_utc_fn: Optional function to get current UTC timestamp (default: None for testing)
    """
    from src.lib import now_utc

    ensure_dir(changelog_path.parent)
    if changelog_path.exists():
        existing = changelog_path.read_text(encoding="utf-8", errors="ignore")
    else:
        existing = "# AI Docs Changelog\n\n"

    timestamp = now_utc_fn() if now_utc_fn else now_utc()
    entry = f"## {timestamp}\n- {summary}\n\n"
    changelog_path.write_text(existing + entry, encoding="utf-8")


def load_previous_metadata(project_dir: Path) -> dict:
    """Load previous metadata.json from .ai-docs directory, or return empty dict."""
    metadata_path = project_dir / ".ai-docs" / "metadata.json"
    if not metadata_path.exists():
        return {}
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def read_json_file(path: Path) -> dict[str, Any]:
    """Safely read a JSON file, returning {} if missing or invalid."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_metadata(project_dir: Path, metadata: dict[str, Any]) -> None:
    """Write metadata.json to the .ai-docs directory."""
    metadata_path = project_dir / ".ai-docs" / "metadata.json"
    ensure_dir(metadata_path.parent)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def gather_existing_markdown_context(
    project_dir: Path,
    max_files: int = 20,
) -> list[dict[str, Any]]:
    """Gather non-generated markdown files for context."""
    generated_roots = {
        "AGENTS.md",
        "AI_DOCS_INDEX.md",
        "CLAUDE.md",
        "CODEX.md",
        "ANTIGRAVITY.md",
    }
    docs: list[dict[str, Any]] = []
    for md_file in sorted(project_dir.rglob("*.md")):
        rel = md_file.relative_to(project_dir).as_posix()
        if rel.startswith(".git/"):
            continue
        if rel.startswith(".ai-docs/"):
            continue
        if rel.startswith(".github/") or rel.startswith(".cursor/"):
            continue
        if rel in generated_roots:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        docs.append({"path": rel, "preview": content[:500].strip()})
        if len(docs) >= max_files:
            break
    return docs
