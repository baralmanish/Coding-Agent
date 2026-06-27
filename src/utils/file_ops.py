"""File I/O and path handling utilities."""

from pathlib import Path
from typing import Any


def read_json_file(path: Path) -> dict[str, Any]:
    """Safely read a JSON file, returning {} if missing."""
    # Extracted from original setup-ai-docs.py line ~853
    raise NotImplementedError("To be extracted from setup-ai-docs.py")


def write_metadata(project_dir: Path, metadata: dict[str, Any]) -> None:
    """Write metadata.json to .ai-docs/ directory."""
    # Extracted from original setup-ai-docs.py line ~1906
    raise NotImplementedError("To be extracted from setup-ai-docs.py")


def gather_existing_markdown_context(
    project_dir: Path,
    max_files: int = 20,
) -> list[dict[str, Any]]:
    """Gather existing markdown files for context."""
    # Extracted from original setup-ai-docs.py line ~1024
    raise NotImplementedError("To be extracted from setup-ai-docs.py")
