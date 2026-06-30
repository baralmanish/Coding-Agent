#!/usr/bin/env python3
"""Run feature-selection matrix tests for ai-docs-bootstrap in CI.

This script validates modular feature behavior:
- Supported feature keys succeed
- Unsupported feature keys fail fast
- enable/disable behavior works
- auto-patch flag activates auto-patch feature
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import tempfile
from itertools import combinations
from pathlib import Path

ALL_FEATURES = [
    "base-docs",
    "agent-docs",
    "feature-specs",
    "custom-agent-config",
    "compliance-level-2",
    "compliance-level-3",
    "ai-analysis",
    "patch-proposals",
    "auto-patch-apply",
    "compliance-dashboard",
    "feature-catalog",
]


def build_cases() -> list[dict]:
    cases: list[dict] = []

    # Single-feature baselines
    for feature in ALL_FEATURES:
        cases.append(
            {
                "name": f"single::{feature}",
                "features": [feature],
                "enable": [],
                "disable": [],
                "expect_ok": True,
            }
        )

    # Deterministic pair coverage (bounded for CI speed)
    for first, second in list(combinations(ALL_FEATURES, 2))[:15]:
        cases.append(
            {
                "name": f"pair::{first}+{second}",
                "features": [first, second],
                "enable": [],
                "disable": [],
                "expect_ok": True,
            }
        )

    # Incremental enable/disable behavior
    cases.extend(
        [
            {
                "name": "enable::catalog_from_base",
                "features": ["base-docs"],
                "enable": ["feature-catalog"],
                "disable": [],
                "expect_ok": True,
                "expect_file": ".ai-docs/FEATURES.md",
            },
            {
                "name": "enable::dashboard_from_base",
                "features": ["base-docs"],
                "enable": ["compliance-dashboard"],
                "disable": [],
                "expect_ok": True,
            },
            {
                "name": "disable::remove_catalog",
                "features": ["base-docs", "feature-catalog"],
                "enable": [],
                "disable": ["feature-catalog"],
                "expect_ok": True,
                "expect_not_file": ".ai-docs/FEATURES.md",
            },
            {
                "name": "disable::remove_dashboard",
                "features": ["base-docs", "compliance-level-3", "compliance-dashboard"],
                "enable": [],
                "disable": ["compliance-dashboard"],
                "expect_ok": True,
                "expect_not_file": ".specs/compliance/dashboard/index.html",
            },
        ]
    )

    # Invalid entries must fail
    cases.extend(
        [
            {
                "name": "invalid::explicit_unknown",
                "features": ["base-docs", "not-real"],
                "enable": [],
                "disable": [],
                "expect_ok": False,
                "expect_error": "Unsupported feature option(s)",
            },
            {
                "name": "invalid::enable_unknown",
                "features": ["base-docs"],
                "enable": ["ghost-feature"],
                "disable": [],
                "expect_ok": False,
                "expect_error": "Unsupported feature option(s)",
            },
            {
                "name": "invalid::disable_unknown",
                "features": ["base-docs"],
                "enable": [],
                "disable": ["ghost-feature"],
                "expect_ok": False,
                "expect_error": "Unsupported feature option(s)",
            },
        ]
    )

    cases.append(
        {
            "name": "autopatch::flag_adds_feature",
            "features": ["base-docs"],
            "enable": [],
            "disable": [],
            "apply_auto_patches": True,
            "expect_ok": True,
            "expect_stdout": "auto-patch-apply",
        }
    )

    return cases


def run_case(bootstrap: str, case: dict) -> tuple[bool, dict | None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = [bootstrap, "--project", temp_dir, "--mode", "new", "--non-interactive"]

        if case.get("features"):
            cmd.extend(["--features", ",".join(case["features"])])
        if case.get("enable"):
            cmd.extend(["--enable-features", ",".join(case["enable"])])
        if case.get("disable"):
            cmd.extend(["--disable-features", ",".join(case["disable"])])
        if case.get("apply_auto_patches"):
            cmd.append("--apply-auto-patches")

        proc = subprocess.run(cmd, capture_output=True, text=True)
        ok = proc.returncode == 0

        if ok != case["expect_ok"]:
            return False, {
                "name": case["name"],
                "reason": f"exit mismatch expected_ok={case['expect_ok']} got_rc={proc.returncode}",
                "cmd": " ".join(shlex.quote(value) for value in cmd),
                "stdout": proc.stdout[-1200:],
                "stderr": proc.stderr[-1200:],
            }

        if case.get("expect_error"):
            stream = f"{proc.stdout}\n{proc.stderr}"
            if case["expect_error"] not in stream:
                return False, {
                    "name": case["name"],
                    "reason": f"missing expected error text: {case['expect_error']}",
                    "cmd": " ".join(shlex.quote(value) for value in cmd),
                    "stdout": proc.stdout[-1200:],
                    "stderr": proc.stderr[-1200:],
                }

        if case.get("expect_stdout") and case["expect_stdout"] not in proc.stdout:
            return False, {
                "name": case["name"],
                "reason": f"missing expected stdout text: {case['expect_stdout']}",
                "cmd": " ".join(shlex.quote(value) for value in cmd),
                "stdout": proc.stdout[-1200:],
                "stderr": proc.stderr[-1200:],
            }

        if case.get("expect_file"):
            expected = os.path.join(temp_dir, case["expect_file"])
            if not os.path.isfile(expected):
                return False, {
                    "name": case["name"],
                    "reason": f"expected file missing: {case['expect_file']}",
                    "cmd": " ".join(shlex.quote(value) for value in cmd),
                    "stdout": proc.stdout[-1200:],
                    "stderr": proc.stderr[-1200:],
                }

        if case.get("expect_not_file"):
            forbidden = os.path.join(temp_dir, case["expect_not_file"])
            if os.path.isfile(forbidden):
                return False, {
                    "name": case["name"],
                    "reason": f"file should not exist: {case['expect_not_file']}",
                    "cmd": " ".join(shlex.quote(value) for value in cmd),
                    "stdout": proc.stdout[-1200:],
                    "stderr": proc.stderr[-1200:],
                }

    return True, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run feature matrix tests for bootstrap")
    parser.add_argument(
        "--bootstrap",
        default="./ai-docs-bootstrap",
        help="Path to ai-docs-bootstrap executable",
    )
    parser.add_argument(
        "--summary-path",
        default=".ci-artifacts/feature-matrix-summary.json",
        help="Path to write matrix summary JSON",
    )
    args = parser.parse_args()

    bootstrap_path = Path(args.bootstrap).resolve()
    if not bootstrap_path.exists():
        print(f"Bootstrap executable not found: {bootstrap_path}")
        return 2

    cases = build_cases()
    failures: list[dict] = []
    passed = 0

    for case in cases:
        ok, failure = run_case(str(bootstrap_path), case)
        if ok:
            passed += 1
        elif failure is not None:
            failures.append(failure)

    summary = {
        "total_cases": len(cases),
        "passed": passed,
        "failed": len(failures),
        "failed_cases": failures,
    }

    summary_path = Path(args.summary_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
