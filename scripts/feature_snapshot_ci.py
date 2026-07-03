#!/usr/bin/env python3
"""Validate golden snapshots for key feature-output combinations.

This script generates docs in temporary directories for a bounded set of
feature combinations, then compares selected output files against fixtures.
It writes:
- JSON summary (for CI parsing)
- Markdown diff hints (for CI artifact review)
"""

from __future__ import annotations

import argparse
import difflib
import json
import shlex
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SnapshotCase:
    name: str
    args: list[str]
    files: list[str]


CASES: list[SnapshotCase] = [
    SnapshotCase(
        name="feature_catalog_base",
        args=[
            "--features",
            "base-docs,feature-catalog",
        ],
        files=[".ai-docs/FEATURES.md"],
    ),
    SnapshotCase(
        name="profile_standard",
        args=[
            "--feature-profile",
            "standard",
        ],
        files=[".ai-docs/FEATURES.md"],
    ),
    SnapshotCase(
        name="compliance_level2_pci",
        args=[
            "--compliance",
            "pci-dss",
            "--compliance-level",
            "2",
            "--features",
            "base-docs,compliance-level-2",
        ],
        files=[".specs/compliance/pci-dss-scanning.md"],
    ),
    SnapshotCase(
        name="compliance_dashboard_level3",
        args=[
            "--compliance",
            "pci-dss",
            "--compliance-level",
            "3",
            "--features",
            "base-docs,compliance-level-3,compliance-dashboard",
        ],
        files=[".specs/compliance/dashboard/index.html"],
    ),
]


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n")


def run_case(bootstrap: Path, case: SnapshotCase) -> tuple[list[dict], str]:
    mismatches: list[dict] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir)
        cmd = [
            str(bootstrap),
            "--project",
            str(project_dir),
            "--mode",
            "new",
            "--non-interactive",
            *case.args,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            mismatches.append(
                {
                    "type": "execution_failed",
                    "case": case.name,
                    "cmd": " ".join(shlex.quote(item) for item in cmd),
                    "stdout": proc.stdout[-1200:],
                    "stderr": proc.stderr[-1200:],
                }
            )
        return mismatches, project_dir.as_posix()


def compare_case(
    bootstrap: Path,
    case: SnapshotCase,
    fixtures_dir: Path,
    update_fixtures: bool,
) -> tuple[bool, list[dict]]:
    failures: list[dict] = []

    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir)
        cmd = [
            str(bootstrap),
            "--project",
            str(project_dir),
            "--mode",
            "new",
            "--non-interactive",
            *case.args,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append(
                {
                    "type": "execution_failed",
                    "case": case.name,
                    "cmd": " ".join(shlex.quote(item) for item in cmd),
                    "stdout": proc.stdout[-1200:],
                    "stderr": proc.stderr[-1200:],
                }
            )
            return False, failures

        for rel_path in case.files:
            generated_path = project_dir / rel_path
            fixture_path = fixtures_dir / case.name / rel_path

            if not generated_path.exists():
                failures.append(
                    {
                        "type": "missing_generated_file",
                        "case": case.name,
                        "file": rel_path,
                        "cmd": " ".join(shlex.quote(item) for item in cmd),
                    }
                )
                continue

            generated_text = normalize_text(
                generated_path.read_text(encoding="utf-8", errors="ignore")
            )

            if update_fixtures:
                fixture_path.parent.mkdir(parents=True, exist_ok=True)
                fixture_path.write_text(generated_text, encoding="utf-8")
                continue

            if not fixture_path.exists():
                failures.append(
                    {
                        "type": "missing_fixture",
                        "case": case.name,
                        "file": rel_path,
                        "fixture": str(fixture_path),
                        "cmd": " ".join(shlex.quote(item) for item in cmd),
                    }
                )
                continue

            expected_text = normalize_text(
                fixture_path.read_text(encoding="utf-8", errors="ignore")
            )
            if expected_text != generated_text:
                diff = "\n".join(
                    difflib.unified_diff(
                        expected_text.splitlines(),
                        generated_text.splitlines(),
                        fromfile=f"fixture:{fixture_path.as_posix()}",
                        tofile=f"generated:{rel_path}",
                        lineterm="",
                    )
                )
                failures.append(
                    {
                        "type": "snapshot_mismatch",
                        "case": case.name,
                        "file": rel_path,
                        "fixture": str(fixture_path),
                        "cmd": " ".join(shlex.quote(item) for item in cmd),
                        "diff": diff,
                    }
                )

    return len(failures) == 0, failures


def write_summary(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_diff_hints(path: Path, failures: list[dict], fixtures_dir: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not failures:
        path.write_text(
            "# Feature Snapshot Diffs\n\nNo snapshot failures detected.\n",
            encoding="utf-8",
        )
        return

    lines = [
        "# Feature Snapshot Diffs",
        "",
        "Regenerate fixtures locally when intentional changes occur:",
        f"`python3 scripts/feature_snapshot_ci.py --bootstrap ./ai-docs-bootstrap --fixtures-dir {fixtures_dir.as_posix()} --update-fixtures`",
        "",
    ]

    for idx, failure in enumerate(failures, start=1):
        lines.append(
            f"## {idx}. {failure.get('case', 'unknown')} :: {failure.get('type', 'failure')}"
        )
        if failure.get("file"):
            lines.append(f"- File: `{failure['file']}`")
        if failure.get("cmd"):
            lines.append(f"- Reproduce: `{failure['cmd']}`")
        if failure.get("fixture"):
            lines.append(f"- Fixture: `{failure['fixture']}`")
        if failure.get("stderr"):
            lines.append("- Stderr tail:")
            lines.append("```")
            lines.append(failure["stderr"])
            lines.append("```")
        if failure.get("diff"):
            lines.append("- Diff:")
            lines.append("```diff")
            lines.append(failure["diff"])
            lines.append("```")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate golden snapshots for feature outputs"
    )
    parser.add_argument(
        "--bootstrap",
        default="./ai-docs-bootstrap",
        help="Path to ai-docs-bootstrap executable",
    )
    parser.add_argument(
        "--fixtures-dir",
        default="tests/snapshots/feature_outputs",
        help="Directory containing snapshot fixtures",
    )
    parser.add_argument(
        "--summary-path",
        default=".ci-artifacts/feature-snapshot-summary.json",
        help="Path to write snapshot summary JSON",
    )
    parser.add_argument(
        "--diff-path",
        default=".ci-artifacts/feature-snapshot-diffs.md",
        help="Path to write markdown diff hints",
    )
    parser.add_argument(
        "--update-fixtures",
        action="store_true",
        help="Update fixture files from current generated outputs",
    )
    args = parser.parse_args()

    bootstrap = Path(args.bootstrap).resolve()
    fixtures_dir = Path(args.fixtures_dir)
    summary_path = Path(args.summary_path)
    diff_path = Path(args.diff_path)

    if not bootstrap.exists():
        payload = {
            "total_cases": len(CASES),
            "passed": 0,
            "failed": len(CASES),
            "failed_cases": [
                {
                    "type": "bootstrap_not_found",
                    "bootstrap": str(bootstrap),
                }
            ],
        }
        write_summary(summary_path, payload)
        write_diff_hints(diff_path, payload["failed_cases"], fixtures_dir)
        print(json.dumps(payload, indent=2))
        return 2

    failed_cases: list[dict] = []
    passed = 0

    for case in CASES:
        ok, failures = compare_case(
            bootstrap=bootstrap,
            case=case,
            fixtures_dir=fixtures_dir,
            update_fixtures=args.update_fixtures,
        )
        if ok:
            passed += 1
        else:
            failed_cases.extend(failures)

    payload = {
        "total_cases": len(CASES),
        "passed": passed,
        "failed": len(failed_cases),
        "updated_fixtures": bool(args.update_fixtures),
        "failed_cases": failed_cases,
    }
    write_summary(summary_path, payload)
    write_diff_hints(diff_path, failed_cases, fixtures_dir)

    print(json.dumps(payload, indent=2))
    return 0 if not failed_cases else 1


if __name__ == "__main__":
    raise SystemExit(main())
