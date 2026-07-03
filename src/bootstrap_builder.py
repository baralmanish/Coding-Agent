"""Bootstrap builder helper utilities.

These helpers are kept in a dedicated module to keep setup-ai-docs.py focused on
orchestration while preserving the generated runtime behavior.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path


def sanitize_feature_name(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-_")
    return cleaned or "feature"


def detect_feature_names(project_dir: Path, max_features: int = 8) -> list[str]:
    roots = ["src", "app", "services", "backend", "frontend"]
    ignore = {
        "node_modules",
        "dist",
        "build",
        "__pycache__",
        "tests",
        "test",
        ".git",
        ".ai-docs",
        ".specs",
        ".github",
        ".cursor",
    }

    candidates = []
    for root_name in roots:
        root = project_dir / root_name
        if not root.exists() or not root.is_dir():
            continue

        for child in sorted(root.iterdir()):
            name = child.name
            if name.startswith(".") or name.lower() in ignore:
                continue
            if child.is_dir():
                candidates.append(name)
                continue
            if child.is_file() and "." in name:
                stem = name.rsplit(".", 1)[0]
                if stem and stem.lower() not in ignore:
                    candidates.append(stem)

    unique = []
    seen = set()
    for name in candidates:
        feature = sanitize_feature_name(name)
        if feature in seen or feature in {"core", "template"}:
            continue
        seen.add(feature)
        unique.append(feature)
        if len(unique) >= max_features:
            break

    return unique


def write_metadata_simple(
    project_dir: Path, ctx: dict, generated_files: list[str]
) -> None:
    """Write generation metadata to disk (simplified version for bootstrap)."""
    metadata_path = project_dir / ".ai-docs" / "metadata.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generator_version": "1.0.0",
        "generated_at": ctx.get("generated_at", ""),
        "target_os": ctx.get("target_os", ""),
        "project_type": ctx.get("project_type", ""),
        "compliance_level": ctx.get("compliance_level", 1),
        "generated_files": generated_files,
    }
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_feature_spec_files(
    feature_names: list[str], locale: str = "en"
) -> tuple[dict[str, str], str]:
    lang = (locale or "en").strip().lower()
    labels = {
        "en": {"spec": "Feature Spec", "memory": "Feature Memory"},
        "es": {
            "spec": "Especificacion de Funcionalidad",
            "memory": "Memoria de Funcionalidad",
        },
        "fr": {
            "spec": "Specification de Fonctionnalite",
            "memory": "Memoire de Fonctionnalite",
        },
    }
    localized = labels.get(lang, labels["en"])
    spec_label = localized["spec"]
    memory_label = localized["memory"]

    files = {}
    index_lines = [
        "---",
        "title: Specs Memory Index",
        "type: specs-index",
        "tags: [ai-docs, specs, knowledge-graph]",
        "---",
        "",
        "# Specs Memory Index",
        "",
        "Track feature specs and where their memory files live.",
        "",
        "## Related Links",
        "- [[.specs/features/core/spec.md]]",
        "- [[.specs/features/core/memory.md]]",
        "",
        "## Index",
        "- core: .specs/features/core/spec.md",
        "- core-memory: .specs/features/core/memory.md",
    ]

    for feature in feature_names:
        spec_path = f".specs/features/{feature}/spec.md"
        memory_path = f".specs/features/{feature}/memory.md"

        files[spec_path] = f"""---
    title: {spec_label} {feature}
type: feature-spec
tags: [ai-docs, specs, knowledge-graph]
related:
  - [[.specs/memory.md]]
  - [[.specs/features/{feature}/memory.md]]
---

    # {spec_label}: {feature}

## Goal
Define expected behavior for {feature}.

## Acceptance Criteria
1. Core behavior for {feature} is defined.
2. Tests can map to acceptance criteria.
3. Security/performance constraints are explicit.

## Test Mapping
- AC1 -> unit/integration tests for {feature}
- AC2 -> acceptance test coverage for {feature}
- AC3 -> security/performance checks

## Linked Notes
- [[.specs/memory.md]]
- [[.specs/features/{feature}/memory.md]]
"""

        files[memory_path] = f"""---
    title: {memory_label} {feature}
type: feature-memory
tags: [ai-docs, memory, knowledge-graph]
related:
  - [[.specs/memory.md]]
  - [[.specs/features/{feature}/spec.md]]
---

    # {memory_label}: {feature}

## Decisions
- <record key implementation and design decisions>

## Open Questions
- <record unresolved questions and follow-ups>

## Linked Notes
- [[.specs/memory.md]]
- [[.specs/features/{feature}/spec.md]]
"""

        index_lines.append(f"- {feature}: {spec_path}")
        index_lines.append(f"- {feature}-memory: {memory_path}")

    index_content = "\n".join(index_lines).rstrip() + "\n"
    return files, index_content


@lru_cache(maxsize=1)
def _prepare_embedded_sources() -> tuple[str, str]:
    """Prepare escaped utility/generator source blobs for bootstrap embedding."""
    current_file = Path(__file__).read_text(encoding="utf-8")
    current_lines = current_file.split("\n")

    utility_functions_code = ""
    i = 0
    while i < len(current_lines):
        line = current_lines[i]
        if (
            line.startswith("def sanitize_feature_name")
            or line.startswith("def detect_feature_names")
            or line.startswith("def write_metadata_simple")
            or line.startswith("def build_feature_spec_files")
        ):
            func_start = i
            i += 1
            while i < len(current_lines):
                if (
                    current_lines[i]
                    and not current_lines[i][0].isspace()
                    and (
                        current_lines[i].startswith("def ")
                        or current_lines[i].startswith("@")
                    )
                ):
                    break
                i += 1
            utility_functions_code += "\n".join(current_lines[func_start:i]) + "\n\n"
        else:
            i += 1

    utility_functions_escaped = (
        json.dumps(utility_functions_code) if utility_functions_code else '""'
    )

    root_dir = Path(__file__).resolve().parent.parent

    generator_code = root_dir / "src" / "generators" / "core.py"
    gen_functions_code = ""
    if generator_code.exists():
        gen_content = generator_code.read_text(encoding="utf-8")
        lines = gen_content.split("\n")
        func_start = None
        for i, line in enumerate(lines):
            if line.startswith("def generate_agents_md"):
                func_start = i
                break
        if func_start is not None:
            gen_functions_code = "\n".join(lines[func_start:])

    compliance_code = root_dir / "src" / "generators" / "compliance.py"
    compliance_functions_code = ""
    if compliance_code.exists():
        comp_content = compliance_code.read_text(encoding="utf-8")
        compliance_functions_code = comp_content

    gen_functions_code += "\n\n" + compliance_functions_code

    file_io_code = root_dir / "src" / "utils" / "file_io.py"
    file_io_functions_code = ""
    if file_io_code.exists():
        file_io_content = file_io_code.read_text(encoding="utf-8")
        lines = file_io_content.split("\n")
        func_start = None
        for i, line in enumerate(lines):
            if line.startswith("def ensure_dir"):
                func_start = i
                break
        if func_start is not None:
            file_io_functions_code = "\n".join(lines[func_start:])
            file_io_functions_code = file_io_functions_code.replace(
                "    from src.lib import now_utc",
                "    # now_utc will be defined in globals() after exec()",
            )

    lib_code = root_dir / "src" / "lib.py"
    now_utc_code = ""
    if lib_code.exists():
        lib_content = lib_code.read_text(encoding="utf-8")
        lines = lib_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("def now_utc"):
                j = i + 1
                while j < len(lines) and (not lines[j] or lines[j][0].isspace()):
                    j += 1
                now_utc_code = "\n".join(lines[i:j]) + "\n"
                break

    gen_functions_code += "\n\n" + now_utc_code + "\n\n" + file_io_functions_code

    gen_functions_escaped = (
        json.dumps(gen_functions_code) if gen_functions_code else '""'
    )

    return utility_functions_escaped, gen_functions_escaped
