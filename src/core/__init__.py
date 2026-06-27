"""Core functionality - context building and project detection."""

from pathlib import Path
from typing import Any


def build_common_context(
    project_dir: Path,
    stack: dict[str, Any] | None = None,
    app_intent: str | None = None,
    compliance_level: int = 1,
    compliance_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Build common context for file generation.

    This function integrates:
    - Project detection and stack analysis
    - App intent resolution
    - Compliance framework selection
    - File generation scope

    Args:
        project_dir: Root directory of the target project
        stack: Detected or provided stack information
        app_intent: Application intent/domain
        compliance_level: Compliance documentation level (0-3)
        compliance_keys: Selected compliance packs

    Returns:
        Complete context dict for file generation
    """
    # This function will be extracted from the original setup-ai-docs.py
    # See lines ~1602-1635 in the original file
    raise NotImplementedError("To be extracted from setup-ai-docs.py")
