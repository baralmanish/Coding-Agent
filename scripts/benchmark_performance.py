#!/usr/bin/env python3
from __future__ import annotations

import argparse
import cProfile
import importlib.machinery
import importlib.util
import io
import json
import pstats
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ALL_COMPLIANCE_PACKS = [
    "pci-dss",
    "hipaa",
    "gdpr",
    "soc2",
    "ccpa",
    "iso27001",
]


@dataclass
class TimingSummary:
    iterations: int
    warmup: int
    min_ms: float
    max_ms: float
    mean_ms: float
    p95_ms: float


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, int(round((p / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]


def summarize(samples_ms: list[float], warmup: int) -> TimingSummary:
    return TimingSummary(
        iterations=len(samples_ms),
        warmup=warmup,
        min_ms=min(samples_ms),
        max_ms=max(samples_ms),
        mean_ms=mean(samples_ms),
        p95_ms=percentile(samples_ms, 95.0),
    )


def load_setup_module(repo_root: Path):
    root_str = str(repo_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    setup_path = repo_root / "setup-ai-docs.py"
    spec = importlib.util.spec_from_file_location("setup_ai_docs", str(setup_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import module from {setup_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_bootstrap_module(repo_root: Path):
    script_path = repo_root / "ai-docs-bootstrap"
    loader = importlib.machinery.SourceFileLoader("ai_docs_bootstrap", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError(f"Unable to build module spec for {script_path}")

    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def run_timed(iterations: int, warmup: int, fn) -> list[float]:
    for _ in range(max(0, warmup)):
        fn()

    samples_ms: list[float] = []
    for _ in range(max(1, iterations)):
        start = time.perf_counter()
        fn()
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        samples_ms.append(elapsed_ms)
    return samples_ms


def profile_once(fn, top_n: int) -> str:
    profiler = cProfile.Profile()
    profiler.enable()
    fn()
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("cumulative")
    stats.print_stats(top_n)
    return stream.getvalue()


def build_new_project_context(bootstrap_module, project_dir: Path) -> dict:
    stack = bootstrap_module.detect_stack(project_dir)
    new_details = {
        "target_os": "macos",
        "app_intent": "general-app",
        "app_intent_input": "general-app",
        "compliance_keys": list(ALL_COMPLIANCE_PACKS),
        "compliance_level": 3,
        "agents": list(bootstrap_module.DEFAULT_AGENTS),
        "languages": [],
        "frameworks": [],
        "tests": [],
        "linting": [],
        "suggestions": [],
    }
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return bootstrap_module.build_common_context(
        "new", stack, new_details, generated_at
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Performance benchmark for setup-ai-docs generator paths."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=12,
        help="Number of measured iterations per benchmark.",
    )
    parser.add_argument(
        "--warmup", type=int, default=3, help="Warmup iterations before measurement."
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Top profile entries to print by cumulative time.",
    )
    parser.add_argument(
        "--output",
        default="benchmarks/performance-baseline.json",
        help="Path for JSON benchmark output (relative to repo root).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    setup_module = load_setup_module(repo_root)
    bootstrap_module = load_bootstrap_module(repo_root)

    prompt_path = repo_root / "master-prompt.md"
    master_prompt = prompt_path.read_text(encoding="utf-8")

    build_samples = run_timed(
        args.iterations,
        args.warmup,
        lambda: setup_module.build_bootstrap_script(master_prompt, "macos"),
    )

    def generate_once() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            ctx = build_new_project_context(bootstrap_module, project_dir)
            markdown_context = bootstrap_module.gather_existing_markdown_context(
                project_dir
            )
            bootstrap_module.generate_files(
                project_dir, ctx, markdown_context, check_mode=False
            )

    generate_samples = run_timed(args.iterations, args.warmup, generate_once)

    build_profile = profile_once(
        lambda: setup_module.build_bootstrap_script(master_prompt, "macos"),
        args.top,
    )
    generate_profile = profile_once(generate_once, args.top)

    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "benchmarks": {
            "build_bootstrap_script_ms": asdict(summarize(build_samples, args.warmup)),
            "generate_files_new_project_ms": asdict(
                summarize(generate_samples, args.warmup)
            ),
        },
        "profiles": {
            "build_bootstrap_script_top": build_profile,
            "generate_files_new_project_top": generate_profile,
        },
    }

    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("Performance benchmark complete.")
    print(f"- Output JSON: {output_path}")

    build_summary = result["benchmarks"]["build_bootstrap_script_ms"]
    generate_summary = result["benchmarks"]["generate_files_new_project_ms"]

    print("\nBenchmark summaries (milliseconds):")
    print(
        "- build_bootstrap_script: "
        f"mean={build_summary['mean_ms']:.2f}, "
        f"p95={build_summary['p95_ms']:.2f}, "
        f"min={build_summary['min_ms']:.2f}, "
        f"max={build_summary['max_ms']:.2f}"
    )
    print(
        "- generate_files (new project, level3/all packs): "
        f"mean={generate_summary['mean_ms']:.2f}, "
        f"p95={generate_summary['p95_ms']:.2f}, "
        f"min={generate_summary['min_ms']:.2f}, "
        f"max={generate_summary['max_ms']:.2f}"
    )

    print("\nTop cumulative profile entries: build_bootstrap_script")
    print(build_profile)
    print("Top cumulative profile entries: generate_files")
    print(generate_profile)


if __name__ == "__main__":
    main()
