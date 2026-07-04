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


def evaluate_changes(changed_files: list[str]) -> dict:
    code_files = sorted({p for p in changed_files if is_code_change(p)})
    traceability_files = sorted({p for p in changed_files if is_traceability_update(p)})
    violations = []

    if code_files and not traceability_files:
        violations.append(
            "Code changes detected without corresponding updates in .specs/, .ai-docs/, AGENTS.md, or AI_DOCS_INDEX.md."
        )

    return {
        "changed_files": sorted(set(changed_files)),
        "code_files": code_files,
        "traceability_files": traceability_files,
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
    result = evaluate_changes(files)
    write_report(args.report_path or None, result)

    print(f"Changed files: {len(result['changed_files'])}")
    print(f"Code files: {len(result['code_files'])}")
    print(f"Traceability files: {len(result['traceability_files'])}")

    if not result["passed"]:
        print("\nSpec traceability gate failed:")
        for violation in result["violations"]:
            print(f"- {violation}")
        print("\nUpdate specs/docs before merging code changes.")
        raise SystemExit(1)

    print("Spec traceability gate passed.")


if __name__ == "__main__":
    main()
