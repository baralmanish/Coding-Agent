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
import time
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

REQUIRED_FEATURES = {
    "ai-analysis": ["compliance-level-3"],
    "patch-proposals": ["compliance-level-3"],
    "auto-patch-apply": ["compliance-level-3"],
    "compliance-dashboard": ["compliance-level-3"],
}

FAST_PAIR_LIMIT = 6
FULL_PAIR_LIMIT = 24
MAX_SLOWEST_CASES = 5
HISTORY_SAMPLE_LIMIT = 50


def with_required_features(features: list[str]) -> list[str]:
    resolved: list[str] = []
    for feature in features:
        for required in REQUIRED_FEATURES.get(feature, []):
            if required not in resolved:
                resolved.append(required)
        if feature not in resolved:
            resolved.append(feature)
    return resolved


def build_cases(tier: str) -> list[dict]:
    cases: list[dict] = []
    pair_limit = FAST_PAIR_LIMIT if tier == "fast" else FULL_PAIR_LIMIT

    # Single-feature baselines
    for feature in ALL_FEATURES:
        feature_set = with_required_features([feature])
        cases.append(
            {
                "name": f"single::{feature}",
                "features": feature_set,
                "enable": [],
                "disable": [],
                "expect_ok": True,
                "apply_auto_patches": feature == "auto-patch-apply",
            }
        )

    # Deterministic pair coverage (bounded by tier)
    for first, second in list(combinations(ALL_FEATURES, 2))[:pair_limit]:
        cases.append(
            {
                "name": f"pair::{first}+{second}",
                "features": with_required_features([first, second]),
                "enable": [],
                "disable": [],
                "expect_ok": True,
                "apply_auto_patches": "auto-patch-apply" in {first, second},
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
                "features": ["base-docs", "compliance-level-3"],
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
                "name": "invalid::dashboard_missing_level3",
                "features": ["base-docs", "compliance-dashboard"],
                "enable": [],
                "disable": [],
                "expect_ok": False,
                "expect_error": "Invalid feature combination(s)",
            },
            {
                "name": "invalid::autopatch_missing_flag",
                "features": ["base-docs", "compliance-level-3", "auto-patch-apply"],
                "enable": [],
                "disable": [],
                "expect_ok": False,
                "expect_error": "--apply-auto-patches",
            },
        ]
    )

    if tier == "full":
        cases.extend(
            [
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
            "features": ["base-docs", "compliance-level-3"],
            "enable": [],
            "disable": [],
            "apply_auto_patches": True,
            "expect_ok": True,
            "expect_stdout": "auto-patch-apply",
        }
    )

    return cases


def run_case(bootstrap: str, case: dict) -> tuple[bool, dict | None, int]:
    started_at = time.perf_counter()
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
        duration_ms = int((time.perf_counter() - started_at) * 1000)

        if ok != case["expect_ok"]:
            return (
                False,
                {
                    "name": case["name"],
                    "reason": f"exit mismatch expected_ok={case['expect_ok']} got_rc={proc.returncode}",
                    "cmd": " ".join(shlex.quote(value) for value in cmd),
                    "stdout": proc.stdout[-1200:],
                    "stderr": proc.stderr[-1200:],
                    "duration_ms": duration_ms,
                },
                duration_ms,
            )

        if case.get("expect_error"):
            stream = f"{proc.stdout}\n{proc.stderr}"
            if case["expect_error"] not in stream:
                return (
                    False,
                    {
                        "name": case["name"],
                        "reason": f"missing expected error text: {case['expect_error']}",
                        "cmd": " ".join(shlex.quote(value) for value in cmd),
                        "stdout": proc.stdout[-1200:],
                        "stderr": proc.stderr[-1200:],
                        "duration_ms": duration_ms,
                    },
                    duration_ms,
                )

        if case.get("expect_stdout") and case["expect_stdout"] not in proc.stdout:
            return (
                False,
                {
                    "name": case["name"],
                    "reason": f"missing expected stdout text: {case['expect_stdout']}",
                    "cmd": " ".join(shlex.quote(value) for value in cmd),
                    "stdout": proc.stdout[-1200:],
                    "stderr": proc.stderr[-1200:],
                    "duration_ms": duration_ms,
                },
                duration_ms,
            )

        if case.get("expect_file"):
            expected = os.path.join(temp_dir, case["expect_file"])
            if not os.path.isfile(expected):
                return (
                    False,
                    {
                        "name": case["name"],
                        "reason": f"expected file missing: {case['expect_file']}",
                        "cmd": " ".join(shlex.quote(value) for value in cmd),
                        "stdout": proc.stdout[-1200:],
                        "stderr": proc.stderr[-1200:],
                        "duration_ms": duration_ms,
                    },
                    duration_ms,
                )

        if case.get("expect_not_file"):
            forbidden = os.path.join(temp_dir, case["expect_not_file"])
            if os.path.isfile(forbidden):
                return (
                    False,
                    {
                        "name": case["name"],
                        "reason": f"file should not exist: {case['expect_not_file']}",
                        "cmd": " ".join(shlex.quote(value) for value in cmd),
                        "stdout": proc.stdout[-1200:],
                        "stderr": proc.stderr[-1200:],
                        "duration_ms": duration_ms,
                    },
                    duration_ms,
                )

    return True, None, duration_ms


def update_duration_history(history_path: Path, run_record: dict) -> dict:
    history = []
    if history_path.exists():
        try:
            loaded = json.loads(history_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = loaded
        except Exception:
            history = []

    history.append(run_record)
    history = history[-HISTORY_SAMPLE_LIMIT:]
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")

    peer_samples = [
        item
        for item in history[:-1]
        if item.get("tier") == run_record.get("tier")
        and isinstance(item.get("duration_ms"), int)
    ]
    baseline = (
        int(sum(item["duration_ms"] for item in peer_samples) / len(peer_samples))
        if peer_samples
        else 0
    )
    current = int(run_record.get("duration_ms") or 0)
    regression_threshold = int(baseline * 1.3) if baseline else 0
    regression = bool(baseline and current > regression_threshold)

    return {
        "samples": len(peer_samples),
        "baseline_duration_ms": baseline,
        "current_duration_ms": current,
        "regression_threshold_ms": regression_threshold,
        "regression": regression,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run feature matrix tests for bootstrap"
    )
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
    parser.add_argument(
        "--history-path",
        default=".ci-artifacts/feature-matrix-duration-history.json",
        help="Path to duration history JSON used for trend tracking",
    )
    parser.add_argument(
        "--tier",
        choices=["fast", "full"],
        default="fast",
        help="Matrix tier to run (fast for PRs, full for main/nightly)",
    )
    args = parser.parse_args()

    bootstrap_path = Path(args.bootstrap).resolve()
    if not bootstrap_path.exists():
        print(f"Bootstrap executable not found: {bootstrap_path}")
        return 2

    cases = build_cases(args.tier)
    failures: list[dict] = []
    passed = 0
    case_durations: list[dict] = []
    run_started_at = time.perf_counter()

    for case in cases:
        ok, failure, duration_ms = run_case(str(bootstrap_path), case)
        case_durations.append({"name": case["name"], "duration_ms": duration_ms})
        if ok:
            passed += 1
        elif failure is not None:
            failures.append(failure)

    total_duration_ms = int((time.perf_counter() - run_started_at) * 1000)
    slowest_cases = sorted(
        case_durations, key=lambda item: item["duration_ms"], reverse=True
    )[:MAX_SLOWEST_CASES]

    history_data = update_duration_history(
        Path(args.history_path),
        {
            "tier": args.tier,
            "duration_ms": total_duration_ms,
            "total_cases": len(cases),
            "failed": len(failures),
            "slowest_cases": slowest_cases,
        },
    )

    summary = {
        "tier": args.tier,
        "total_cases": len(cases),
        "passed": passed,
        "failed": len(failures),
        "duration_ms": total_duration_ms,
        "slowest_cases": slowest_cases,
        "duration_trend": history_data,
        "failed_cases": failures,
    }

    summary_path = Path(args.summary_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
