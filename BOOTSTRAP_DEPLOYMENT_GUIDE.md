# Bootstrap Deployment Guide

## Purpose

This guide explains how to build, distribute, and run the ai-docs bootstrap executable.

## Build Bootstrap

Run from repository root.

```bash
/opt/homebrew/bin/python3 setup-ai-docs.py
```

Choose target OS profile when prompted:

- macOS
- Linux
- Windows
- Auto

Output:

- ai-docs-bootstrap for macOS/Linux/Auto
- ai-docs-bootstrap.py for Windows profile

## Local Distribution

Copy bootstrap into a target repository and execute there.

```bash
cp /absolute/path/to/Coding\ Agent/ai-docs-bootstrap .
chmod +x ai-docs-bootstrap
./ai-docs-bootstrap --project .
```

Windows profile usage:

```bash
python ai-docs-bootstrap.py --project C:\\path\\to\\repo
```

## Remote Distribution from GitHub

```bash
curl -fsSL https://raw.githubusercontent.com/baralmanish/Coding-Agent/main/ai-docs-bootstrap -o ai-docs-bootstrap
chmod +x ai-docs-bootstrap
./ai-docs-bootstrap --project .
```

## Recommended Release Process

1. Regenerate bootstrap after source changes.
2. Run unit and integration tests.
3. Run benchmark script when performance-sensitive code changes.
4. Commit both source changes and generated bootstrap together.
5. Tag release or publish changelog notes.

## CI Integration

Freshness check example:

```bash
./ai-docs-bootstrap --project /path/to/project --mode existing --check
```

With stale report artifact:

```bash
./ai-docs-bootstrap --project /path/to/project --mode existing --check --report-path .ai-docs-check-report.md
```

Exit codes:

- 0 means docs are up to date
- 1 means docs are stale
- 2 means invalid invocation for interactive-only new mode

## Configuration Flags

Common options:

- --project path to target repository
- --mode auto|new|existing
- --check for verification mode without writes
- --non-interactive for CI-friendly new mode
- --intent for non-interactive intent selection
- --compliance for explicit compliance packs
- --compliance-level 0 to 3

Catalog options:

- --list-stack-presets
- --list-intents
- --list-compliance

## Operational Checklist

Before distributing a new bootstrap:

1. Verify bootstrap rebuild completed successfully.
2. Verify tests pass.
3. Verify generated bootstrap file is executable on unix profiles.
4. Verify key CLI flows:
   - default run
   - check mode
   - non-interactive mode
5. Verify metadata and changelog behavior in a sample target project.

## Troubleshooting

- If generated docs look stale unexpectedly, rerun with --check and inspect stale reasons.
- If compliance files are missing, verify --compliance and --compliance-level values.
- If stack detection appears wrong, inspect manifests in target repo and update detection logic in source.
