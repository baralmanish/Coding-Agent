"""Core orchestration for AI docs generation."""

from src.core.generation import (
    build_common_context,
    determine_impacted_files,
    write_metadata,
)

__all__ = [
    "build_common_context",
    "determine_impacted_files",
    "write_metadata",
]
