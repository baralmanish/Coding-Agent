"""File generators for AI documentation.

This package contains modular generators for creating documentation files:
- core: AGENTS.md, APP-BLUEPRINT.md, AI_DOCS_INDEX.md, CONTEXT-SNAPSHOT.md, etc.
- compliance: Compliance-specific scanning rules (.specs/compliance/*.md)
"""

from .core import (
    generate_agents_md,
    generate_app_blueprint_md,
    generate_index_md,
    generate_context_snapshot,
    generate_agent_specific_docs,
)
from .compliance import (
    generate_level_2_compliance_scanning,
    generate_level_3_compliance_patterns,
)

__all__ = [
    "generate_agents_md",
    "generate_app_blueprint_md",
    "generate_index_md",
    "generate_context_snapshot",
    "generate_agent_specific_docs",
    "generate_level_2_compliance_scanning",
    "generate_level_3_compliance_patterns",
]
