"""CLI/runtime helper template section for ai-docs-bootstrap."""

from __future__ import annotations


def render_runtime_cli() -> str:
    return f'''\

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AI agent markdown docs for a project.")
    parser.add_argument("--project", default=".", help="Target project directory (default: current directory)")
    parser.add_argument(
        "--mode",
        choices=["auto", "new", "existing"],
        default="auto",
        help="Project mode detection override",
    )
    parser.add_argument("--check", action="store_true", help="Check mode: do not write files, exit non-zero if docs are out of date.")
    parser.add_argument("--dry-run", action="store_true", help="Preview generated file changes without writing files.")
    parser.add_argument("--non-interactive", action="store_true", help="Use defaults for prompts in new-project mode.")
    parser.add_argument("--intent", help="Optional app intent for new-project mode (useful for CI/non-interactive runs).")
    parser.add_argument(
        "--compliance",
        help="Optional comma-separated compliance packs for new-project mode (e.g. pci-dss,soc2,gdpr).",
    )
    parser.add_argument(
        "--compliance-level",
        help="Optional compliance documentation level for new-project mode (0=skip, 1=checklists, 2=scanning, 3=patterns).",
    )
    parser.add_argument(
        "--locale",
        default="en",
        help="Locale for generated docs (en/es/fr).",
    )
    parser.add_argument(
        "--compliance-region",
        help="Optional compliance regional variant (us/eu/apac/latam).",
    )
    parser.add_argument(
        "--apply-auto-patches",
        action="store_true",
        help="Apply deterministic Level 3 auto-patch remediations (explicit opt-in).",
    )
    parser.add_argument(
        "--patch-allowlist",
        help="Comma-separated relative path prefixes where auto-patches are allowed (default: src,app,services).",
    )
    parser.add_argument(
        "--patch-denylist",
        help="Comma-separated relative path prefixes where auto-patches are blocked (default includes tests,node_modules,dist,build).",
    )
    parser.add_argument(
        "--custom-frameworks",
        help="Optional comma-separated custom frameworks for new-project mode.",
    )
    parser.add_argument(
        "--custom-config",
        help="Optional JSON file path defining custom_frameworks, custom_compliance_rules, and custom_feature_templates.",
    )
    parser.add_argument("--list-stack-presets", action="store_true", help="Print available stack presets and exit.")
    parser.add_argument("--list-intents", action="store_true", help="Print starter and keyword-mapped intent profiles and exit.")
    parser.add_argument("--list-compliance", action="store_true", help="Print available compliance packs and exit.")
    parser.add_argument("--list-feature-profiles", action="store_true", help="Print available feature profiles and exit.")
    parser.add_argument("--list-features", action="store_true", help="Print available modular feature options and defaults.")
    parser.add_argument("--feature-profile", help="Named feature profile for this run (e.g. minimal, standard, compliance-heavy).")
    parser.add_argument("--features", help="Comma-separated explicit feature set for this run.")
    parser.add_argument("--enable-features", help="Comma-separated features to enable in addition to defaults/explicit set.")
    parser.add_argument("--disable-features", help="Comma-separated features to disable for this run.")
    parser.add_argument("--features-config", help="Optional JSON feature config file to import feature selection inputs.")
    parser.add_argument("--write-features-config", help="Optional JSON path to export the resolved active feature set for repeatable runs.")
    parser.add_argument("--version", action="store_true", help="Print generator version and release highlights.")
    parser.add_argument("--json-report-path", help="Optional path to write structured JSON run report.")
    parser.add_argument("--track-performance", action="store_true", help="Track run duration history and flag regressions.")
    parser.add_argument("--performance-history-path", default="benchmarks/performance-history.json", help="Path for performance history JSON when --track-performance is enabled.")
    parser.add_argument("--context-max-files", type=int, default=20, help="Maximum markdown files to include in context scan (1-200).")
    parser.add_argument("--context-preview-chars", type=int, default=500, help="Preview chars per markdown file in context scan (100-8000).")
    parser.add_argument("--session-state-path", default=".ai-docs/session-state.json", help="Path to write short-term session state for the latest run.")
    parser.add_argument("--report-path", help="Optional path to write markdown report in --check mode.")
    return parser.parse_args()

'''
