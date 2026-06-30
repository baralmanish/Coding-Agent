"""Utility functions for text processing and file I/O."""

from .file_io import (
    ensure_dir,
    write_text,
    read_text_if_exists,
    normalize_text,
    append_changelog,
    load_previous_metadata,
    read_json_file,
    write_metadata,
    gather_existing_markdown_context,
)
from .text import keyword_confidence_score, merge_unique, slugify_intent_key

__all__ = [
    # File I/O
    "ensure_dir",
    "write_text",
    "read_text_if_exists",
    "normalize_text",
    "append_changelog",
    "load_previous_metadata",
    # File operations
    "read_json_file",
    "write_metadata",
    "gather_existing_markdown_context",
    # Text utilities
    "slugify_intent_key",
    "merge_unique",
    "keyword_confidence_score",
]
