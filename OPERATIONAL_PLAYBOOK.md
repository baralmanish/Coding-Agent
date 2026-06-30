# Operational Playbook

This document captures day-2 operations for running and maintaining `ai-docs-bootstrap` safely in local and CI environments.

## 1. Troubleshooting Guide

### 1.1 Bootstrap generation fails

Symptoms:

- `setup-ai-docs.py` exits with syntax/template errors.
- Generated `ai-docs-bootstrap` missing expected helpers.

Checks:

1. Run `python3 -m py_compile setup-ai-docs.py`.
2. Rebuild bootstrap: `printf '4\n' | python3 setup-ai-docs.py`.
3. Run tests: `python3 -m unittest discover -s tests -p 'test_*.py'`.

Fix strategy:

- If failure is in template string sections, verify brace escaping in embedded code blocks.
- If failure is import-related, ensure source function exists in `src/` and embedding extraction still targets the right `def` start marker.

### 1.2 Check mode reports stale files unexpectedly

Symptoms:

- `--check` returns stale list even after generation.

Checks:

1. Run: `./ai-docs-bootstrap --project . --mode existing --check --report-path .ai-docs-check-report.md`.
2. Compare reported files against `.ai-docs/metadata.json` and current generated set.
3. Verify no partial writes or interrupted previous generation.

Fix strategy:

- Regenerate once in non-check mode.
- Re-run check mode.
- If persistent, inspect stale reasons in report and update source-of-truth templates.

### 1.3 Compliance outputs missing

Symptoms:

- No Level 2/3 compliance files generated.

Checks:

1. Confirm `--compliance` values use supported keys.
2. Confirm `--compliance-level` is `2` or `3`.
3. Confirm target project has writable `.specs/compliance` path.

Fix strategy:

- Re-run with explicit flags:
  `./ai-docs-bootstrap --project <path> --mode new --non-interactive --compliance "pci-dss,gdpr" --compliance-level 3`

### 1.4 Auto-patch behavior surprises

Symptoms:

- Patch results not applied where expected, or patching too broad.

Checks:

1. Confirm `--apply-auto-patches` is explicitly set.
2. Review `--patch-allowlist` and `--patch-denylist`.
3. Inspect dry-run proposal output before apply mode.

Fix strategy:

- Start with narrow allowlist (`src`) and explicit denylist (`tests,node_modules,build,dist`).
- Run with dry-run first, then apply.

## 2. Security Review Checklist (Auto-Patch)

Before enabling apply mode in CI or production repositories:

1. Scope controls

- [ ] Allowlist configured to trusted source paths only.
- [ ] Denylist includes tests, vendor dirs, generated dirs, and lockfiles.

2. Change review

- [ ] Dry-run patch proposals reviewed by maintainers.
- [ ] Applied patch report retained as artifact.
- [ ] PR review required for applied changes.

3. Execution safety

- [ ] Scan/pattern limits and timeouts enabled (default hardening).
- [ ] No secrets or credentials in custom config payloads.
- [ ] CI tokens have least privilege.

4. Audit trail

- [ ] JSON run report stored for each CI run.
- [ ] Performance history tracked for anomalies/regressions.
- [ ] Changelog/metadata retained in repository outputs.

## 3. Upgrade and Migration Notes

### 3.1 Safe upgrade workflow

1. Pull latest generator source.
2. Rebuild bootstrap (`setup-ai-docs.py`).
3. Run full tests.
4. Run smoke checks:
   - `--version`
   - `--dry-run`
   - `--check`
5. Regenerate docs in a sample target repository.
6. Validate no unexpected file churn.
7. Package release and checksum with `scripts/package_release.sh`.

### 3.2 Version transition checklist

From older releases to current:

- [ ] Validate new CLI flags do not break existing CI invocation.
- [ ] Add defaults for newly introduced options in pipeline scripts.
- [ ] Validate generated compliance dashboard and analysis artifacts are accepted in downstream tooling.
- [ ] Re-baseline performance history after major feature additions.

### 3.3 Rollback guidance

If a release introduces regressions:

1. Revert to last known good bootstrap artifact.
2. Re-run check mode to verify stability.
3. Open issue with:
   - command used
   - stderr/stdout logs
   - stale report (if any)
   - changed file list

## 4. On-Call Triage Template

When opening an internal incident for generator failures, include:

- Environment (OS, Python version)
- Command executed
- Exit code
- Error snippet
- Affected repository path
- Whether issue reproduces in `--dry-run` and `--check`
- Link to run JSON report artifact
