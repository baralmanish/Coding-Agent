# Contributing

Thanks for contributing to AI Docs Generator.

## Scope

Contributions should improve one or more of these areas:

- Bootstrap generation quality
- Deterministic docs freshness checks
- Stack detection and presets
- CI reliability and report clarity
- Documentation accuracy

## Local Setup

1. Ensure Python 3.11+ is installed.
2. From repository root, run:

```bash
make build-bootstrap
make compile
```

## Development Workflow

1. Create a focused branch.
2. Make small, reviewable changes.
3. Run validation:

```bash
make smoke-check
```

4. If your change touches check/report behavior, run:

```bash
make stale-report
```

5. Update docs when behavior changes:

- README.md
- master-prompt.md (if prompt contract changed)
- .github/workflows/ai-docs-freshness.yml (if CI contract changed)

## Pull Request Guidelines

Include in your PR description:

- What changed
- Why it changed
- Validation commands run
- Any migration notes for users or CI

Keep PRs focused. Avoid bundling unrelated refactors.

## Release Safety

Before release or merge of significant behavior changes:

```bash
make release-check
```

If needed, run with a custom temp dir:

```bash
make release-check TMP_DIR=/tmp/ai-docs-release
```

## Coding Notes

- Preserve deterministic behavior for --check mode.
- Prefer additive and backward-compatible CLI changes.
- Do not break existing generated-file contracts without documenting migration.
- Keep changes readable and explicit over clever.

## Documentation Policy

If a CLI flag, generated file set, or CI behavior changes, update README and this file in the same PR.
