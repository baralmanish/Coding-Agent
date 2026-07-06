#!/usr/bin/env python3
"""Optional CI gate for docs/specs-first workflow.

This gate checks changed files between two commits and fails when code changes
occur without corresponding updates to specs/docs traceability files.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

CODE_PREFIXES = (
    "src/",
    "app/",
    "services/",
    "backend/",
    "frontend/",
)

CODE_SUFFIXES = (
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".cs",
    ".php",
    ".rb",
)

TRACEABILITY_PREFIXES = (
    ".specs/",
    ".ai-docs/",
)

TRACEABILITY_FILES = {
    "AGENTS.md",
    "AI_DOCS_INDEX.md",
}

FEATURE_SPEC_PREFIX = ".specs/features/"
FEATURE_SPEC_SUFFIX = "/spec.md"

REQUIRED_SPEC_MARKERS = (
    "## Spec Enrollment Checklist (Mandatory)",
    "## Goal",
    "## Acceptance Criteria",
    "## Test Mapping",
    "## Traceability Matrix",
)

NORMALIZED_SPEC_DIR = "spec"
NORMALIZED_REQUIRED_FILES = (
    "index.md",
    "acceptance-criteria.md",
    "test-mapping.md",
    "traceability-matrix.md",
)
CHECKLIST_ITEM_PREFIX = "- [ ]"


def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def is_code_change(path: str) -> bool:
    norm = path.replace("\\", "/")
    if norm.startswith(TRACEABILITY_PREFIXES):
        return False
    if norm.startswith(CODE_PREFIXES):
        return True
    return norm.endswith(CODE_SUFFIXES)


def is_traceability_update(path: str) -> bool:
    norm = path.replace("\\", "/")
    return norm.startswith(TRACEABILITY_PREFIXES) or norm in TRACEABILITY_FILES


def is_feature_spec_file(path: str) -> bool:
    norm = path.replace("\\", "/")
    return norm.startswith(FEATURE_SPEC_PREFIX) and norm.endswith(FEATURE_SPEC_SUFFIX)


def validate_feature_spec_file(path: str) -> list[str]:
    file_path = Path(path)
    if not file_path.exists():
        return [f"Missing feature spec file: {path}"]

    content = file_path.read_text(encoding="utf-8")
    violations = []
    for marker in REQUIRED_SPEC_MARKERS:
        if marker not in content:
            violations.append(f"{path}: missing required section '{marker}'")
    return violations


def _extract_checklist_lines(content: str) -> list[str]:
    lines = content.splitlines()
    in_checklist = False
    checklist_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped == "## Spec Enrollment Checklist (Mandatory)":
            in_checklist = True
            continue
        if in_checklist and stripped.startswith("## "):
            break
        if in_checklist and (stripped.startswith("- [") or stripped.startswith("* [")):
            checklist_lines.append(stripped)

    return checklist_lines


def validate_checklist_completion(path: str) -> list[str]:
    content = Path(path).read_text(encoding="utf-8")
    checklist_lines = _extract_checklist_lines(content)
    if not checklist_lines:
        return [f"{path}: checklist section found but no checklist items were detected"]

    remaining = [line for line in checklist_lines if CHECKLIST_ITEM_PREFIX in line]
    if not remaining:
        return []

    return [
        f"{path}: strict mode requires checklist completion; unchecked items: {len(remaining)}"
    ]


def is_spec_oversized(path: str, *, max_spec_lines: int, max_spec_bytes: int) -> bool:
    p = Path(path)
    content = p.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    byte_count = len(content.encode("utf-8"))
    return line_count > max_spec_lines or byte_count > max_spec_bytes


def validate_spec_normalization(path: str) -> list[str]:
    spec_path = Path(path)
    feature_dir = spec_path.parent
    normalized_dir = feature_dir / NORMALIZED_SPEC_DIR
    missing_files = [
        name
        for name in NORMALIZED_REQUIRED_FILES
        if not (normalized_dir / name).exists()
    ]
    if not missing_files:
        return []

    return [
        (
            f"{path}: spec is oversized; normalize into {normalized_dir.as_posix()}/ with files "
            f"{', '.join(NORMALIZED_REQUIRED_FILES)}"
        )
    ]


def evaluate_changes(
    changed_files: list[str],
    *,
    strict_mode: bool = False,
    max_spec_lines: int = 400,
    max_spec_bytes: int = 24_000,
) -> dict:
    code_files = sorted({p for p in changed_files if is_code_change(p)})
    traceability_files = sorted({p for p in changed_files if is_traceability_update(p)})
    feature_spec_files = sorted({p for p in changed_files if is_feature_spec_file(p)})
    violations = []

    if code_files and not traceability_files:
        violations.append(
            "Code changes detected without corresponding updates in .specs/, .ai-docs/, AGENTS.md, or AI_DOCS_INDEX.md."
        )

    if code_files and not feature_spec_files:
        violations.append(
            "Code changes detected without feature spec updates under .specs/features/<feature>/spec.md."
        )

    for path in feature_spec_files:
        violations.extend(validate_feature_spec_file(path))
        if strict_mode and Path(path).exists():
            violations.extend(validate_checklist_completion(path))
            if is_spec_oversized(
                path,
                max_spec_lines=max_spec_lines,
                max_spec_bytes=max_spec_bytes,
            ):
                violations.extend(validate_spec_normalization(path))

    return {
        "changed_files": sorted(set(changed_files)),
        "code_files": code_files,
        "traceability_files": traceability_files,
        "feature_spec_files": feature_spec_files,
        "strict_mode": strict_mode,
        "max_spec_lines": max_spec_lines,
        "max_spec_bytes": max_spec_bytes,
        "passed": len(violations) == 0,
        "violations": violations,
    }


def changed_files_between(base_sha: str, head_sha: str) -> list[str]:
    cmd = ["git", "diff", "--name-only", f"{base_sha}..{head_sha}"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(
            f"Unable to diff commits {base_sha}..{head_sha}: {result.stderr.strip() or result.stdout.strip()}"
        )

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def write_report(path_value: str | None, payload: dict) -> None:
    if not path_value:
        return
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Optional docs/specs-first gate for CI workflows."
    )
    parser.add_argument(
        "--enabled",
        default="false",
        help="Enable gate (true/false).",
    )
    parser.add_argument("--base-sha", default="", help="Base commit SHA for diff.")
    parser.add_argument("--head-sha", default="", help="Head commit SHA for diff.")
    parser.add_argument(
        "--report-path",
        default="",
        help="Optional JSON report output path.",
    )
    parser.add_argument(
        "--strict-mode",
        default="false",
        help="Enable strict checks (checklist completion + oversized spec normalization).",
    )
    parser.add_argument(
        "--max-spec-lines",
        type=int,
        default=400,
        help="Maximum lines in spec.md before normalization is required in strict mode.",
    )
    parser.add_argument(
        "--max-spec-bytes",
        type=int,
        default=24000,
        help="Maximum bytes in spec.md before normalization is required in strict mode.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not _to_bool(args.enabled):
        print("Spec traceability gate disabled; skipping.")
        return

    base_sha = (args.base_sha or "").strip()
    head_sha = (args.head_sha or "").strip()

    if not base_sha or not head_sha:
        print("Spec traceability gate enabled, but commit SHAs are missing. Skipping.")
        return

    files = changed_files_between(base_sha, head_sha)
    strict_mode = _to_bool(args.strict_mode)
    result = evaluate_changes(
        files,
        strict_mode=strict_mode,
        max_spec_lines=max(1, int(args.max_spec_lines)),
        max_spec_bytes=max(1, int(args.max_spec_bytes)),
    )
    write_report(args.report_path or None, result)

    print(f"Changed files: {len(result['changed_files'])}")
    print(f"Code files: {len(result['code_files'])}")
    print(f"Traceability files: {len(result['traceability_files'])}")
    print(f"Strict mode: {str(result['strict_mode']).lower()}")

    if not result["passed"]:
        print("\nSpec traceability gate failed:")
        for violation in result["violations"]:
            print(f"- {violation}")
        print("\nUpdate specs/docs before merging code changes.")
        raise SystemExit(1)

    print("Spec traceability gate passed.")


if __name__ == "__main__":
    main()
