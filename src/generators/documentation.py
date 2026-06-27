"""Documentation generators - blueprint, specs, and other markdown files."""

from pathlib import Path
from typing import Any


def generate_app_blueprint_md(
    project_dir: Path,
    context: dict[str, Any],
    compliance_packs: list[dict[str, Any]] | None = None,
) -> None:
    """Generate APP-BLUEPRINT.md with architecture guidance and compliance checklists.

    Creates `.ai-docs/APP-BLUEPRINT.md` with:
    - Project overview and architecture guidance
    - Agent descriptions and capabilities
    - Compliance checklists for selected packs

    Args:
        project_dir: Target project root
        context: Project context
        compliance_packs: List of selected compliance pack definitions
    """
    # Extracted from lines ~1700-1800 in original setup-ai-docs.py
    raise NotImplementedError("To be extracted from setup-ai-docs.py")
