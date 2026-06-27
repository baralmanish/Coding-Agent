# AI Docs Generator

Generate and maintain AI-agent guidance files for any software project.

This repository provides:

- A master prompt template in `master-prompt.md`
- A builder script in `setup-ai-docs.py`
- A generated drop-in executable (`ai-docs-bootstrap` on macOS/Linux, or `ai-docs-bootstrap.py` for Windows profile)
- CI freshness workflow in `.github/workflows/ai-docs-freshness.yml`

## What It Solves

The bootstrap scans a target project and creates standardized AI documentation for:

- Cursor
- GitHub Copilot
- Claude Code
- OpenAI Codex
- Antigravity
- Shared cross-agent documentation and governance files

It supports:

- New vs existing project detection
- Stack detection from common manifests (`package.json`, `pyproject.toml`, `composer.json`, `Package.swift`, etc.)
- Prompted onboarding for new projects
- Stack presets for common setups
- Starter app-intent profiles (`general-app`, `chatbot`, `crm`) plus any custom intent (for example analytics, crash-logger, social, ewallet, chat-app, ride-booking, ecommerce, scraper, gaming, travel, legal-tech, gov-tech, ad-tech)
- Deterministic freshness checks for CI
- Stale report output for review artifacts
- User-custom section preservation across regenerations

## Requirements

- Python 3.11+ (recommended)
- A project directory where docs will be generated

## Repository Structure

- `master-prompt.md`: canonical prompt used by the builder
- `setup-ai-docs.py`: generates executable bootstrap from the prompt
- `ai-docs-bootstrap`: generated executable (macOS/Linux/auto profile)
- `Makefile`: one-command automation for build/check/smoke/release flows
- `.github/workflows/ai-docs-freshness.yml`: optional CI check workflow
- `.github/pull_request_template.md`: pull request checklist
- `.github/ISSUE_TEMPLATE/*`: bug and feature request templates

## Makefile Shortcuts

Use the included `Makefile` to run common tasks quickly:

```bash
make help
make build-bootstrap
make compile
make smoke
make check-bootstrap
make smoke-check
make stale-report
make release-check
```

To use a custom temp directory:

```bash
make smoke TMP_DIR=/tmp/my-ai-docs
```

## Quick Start

1. Build the bootstrap executable:

```bash
python3 setup-ai-docs.py
```

2. Choose target OS profile when prompted:

- macOS
- Linux
- Windows
- Auto (recommended)

3. Run bootstrap against a target project:

```bash
./ai-docs-bootstrap --project /path/to/project
```

For Windows profile output:

```bash
python ai-docs-bootstrap.py --project C:\path\to\project
```

### Drop-In Quick Start (Other Repos)

From another local repo on the same machine:

```bash
cp /absolute/path/to/Coding\ Agent/ai-docs-bootstrap . && chmod +x ai-docs-bootstrap && ./ai-docs-bootstrap --project .
```

From GitHub (macOS/Linux):

```bash
curl -fsSL https://raw.githubusercontent.com/baralmanish/Coding-Agent/main/ai-docs-bootstrap -o ai-docs-bootstrap && chmod +x ai-docs-bootstrap && ./ai-docs-bootstrap --project .
```

## Usage

### Auto mode (default)

```bash
./ai-docs-bootstrap --project /path/to/project
```

### Force mode

```bash
./ai-docs-bootstrap --project /path/to/project --mode new
./ai-docs-bootstrap --project /path/to/project --mode existing
```

### CI freshness check

```bash
./ai-docs-bootstrap --project /path/to/project --mode existing --check
```

Exit codes:

- `0`: docs are up to date
- `1`: docs are stale
- `2`: invalid check invocation for interactive new-project flow

### Non-interactive new mode

```bash
./ai-docs-bootstrap --project /path/to/project --mode new --non-interactive
```

### Non-interactive with intent/compliance (CI-friendly)

```bash
./ai-docs-bootstrap \
   --project /path/to/project \
   --mode new \
   --non-interactive \
   --intent "ride booking ecommerce payments" \
   --compliance "soc2,gdpr"
```

Notes:

- `--intent` accepts any free-text app intent.
- `--compliance` accepts comma-separated keys: `pci-dss,hipaa,soc2,gdpr,ccpa,iso27001`.
- Intent ranking in `.ai-docs/APP-BLUEPRINT.md` uses confidence scoring and stack-aware tie-breaks.

### Write stale report (for CI artifacts)

```bash
./ai-docs-bootstrap --project /path/to/project --mode existing --check --report-path .ai-docs-check-report.md
```

### Discover available options (no prompts)

```bash
./ai-docs-bootstrap --list-stack-presets
./ai-docs-bootstrap --list-intents
./ai-docs-bootstrap --list-compliance
```

## Stack Presets

In new-project onboarding, you can select:

- `react-ts`
- `next-ts`
- `node-api`
- `express-ts`
- `fastify-ts`
- `nestjs`
- `angular`
- `vue`
- `react-native`
- `nuxt`
- `sveltekit`
- `laravel`
- `django`
- `go-fiber`
- `spring-boot`
- `dotnet-webapi`
- `swift-vapor`
- `swift-ios`
- `fastapi`

Preset values are merged with manually entered languages/frameworks/tests/linting.
The displayed preset list in CLI is generated dynamically from `STACK_PRESETS`.

### App Intents

In new-project onboarding, you can pick a starter app intent profile:

- `general-app`
- `chatbot`
- `crm`

You can also enter any custom app intent (for example: analytics, crash-logger, social-app, ewallet, whatsapp-style chat, ride-booking, ecommerce, scraper, gaming, travel, legal-tech, gov-tech, ad-tech, or anything else). The generator maps known keywords to targeted guidance and falls back to strong general defaults when no keyword matches.

When multiple intent keywords are present, the generator ranks matched domains and shows scoring in `.ai-docs/APP-BLUEPRINT.md`.

You can optionally add compliance packs during onboarding:

- `pci-dss`
- `hipaa`
- `soc2`
- `gdpr`
- `ccpa`
- `iso27001`

Compliance can also be auto-suggested from app intent keywords (for example, wallet/payments -> PCI DSS, health -> HIPAA, social/ad-tech -> GDPR/CCPA, enterprise SaaS -> SOC 2/ISO 27001).

The generated blueprint also includes:

- Recommended package set aligned to current ecosystem standards for detected stack/frameworks
- Stale/deprecated package warnings with modern alternatives
- Security audit command checklist to run before installing new dependencies

This adds targeted implementation guidance and generates `.ai-docs/APP-BLUEPRINT.md` with capability checklists and stack-specific notes (React/Node/Laravel/Python).

## Generated Output

Typical files include:

- `AGENTS.md`
- `AI_DOCS_INDEX.md`
- `.cursor/rules/project.mdc`
- `.github/copilot-instructions.md`
- `CLAUDE.md`
- `CODEX.md`
- `ANTIGRAVITY.md`
- `.ai-docs/CONTEXT-SNAPSHOT.md`
- `.ai-docs/APP-BLUEPRINT.md`
- `.ai-docs/FEEDBACK.md`
- `.ai-docs/ROADMAP.md`
- `.ai-docs/SECURITY.md`
- `.ai-docs/SPEC-DRIVEN-DEVELOPMENT.md`
- `.ai-docs/CHANGELOG.md`
- `.ai-docs/metadata.json`
- `.ai-docs/MASTER_PROMPT_REFERENCE.md`

## Customization Safety

Generated markdown supports preserving user custom content blocks:

```md
<!-- user-custom:start:local -->

Your team-specific guidance here.

<!-- user-custom:end:local -->
```

These blocks are preserved during regeneration.

## CI Integration

This repository includes `.github/workflows/ai-docs-freshness.yml`:

- Builds bootstrap during CI
- Skips freshness checks if AI docs are not initialized
- Runs `--check` mode
- Uploads stale report artifact when docs are outdated
- Fails workflow when stale docs are detected

## Common Workflow

1. Run bootstrap after major stack/tooling changes.
2. Review generated doc diffs.
3. Keep team-specific notes inside user-custom blocks.
4. Use `--check` mode in CI to enforce freshness.

## Developer-Friendly Tips

- For CI/non-interactive setup, use `--intent` and `--compliance` to avoid prompts.
- Run discovery flags (`--list-*`) before choosing presets/intents.
- Review `.ai-docs/APP-BLUEPRINT.md` first; it now includes ranked intents, package recommendations, stale-package warnings, and security-audit commands.

## Troubleshooting

- If check mode fails unexpectedly, regenerate docs once and rerun check.
- For brand-new temporary projects, run one extra generation pass before `--check` (the `make smoke`/`make doctor` flows already do this).
- If running new-project checks in CI, add `--non-interactive` or force `--mode existing`.
- If Python cannot import `tomllib`, use Python 3.11+.

## Release Checklist

Before tagging or publishing changes to this generator, run:

1. Run automated pre-release flow:
   - `make release-check`
2. Confirm CI workflow is still valid:
   - `.github/workflows/ai-docs-freshness.yml`
3. Optional manual breakdown (if you need step-by-step):
   - `make build-bootstrap`
   - `make compile`
   - `make smoke`
   - `make check-bootstrap`
   - `make stale-report`

## Changelog Policy

Use clear, generator-focused changelog entries:

- Include: feature, fix, and behavior changes that affect generated output
- Include: CLI flag additions/changes (`--check`, `--non-interactive`, `--report-path`, etc.)
- Include: CI contract changes (exit code behavior, artifact names, skip logic)
- Exclude: purely cosmetic README wording tweaks unless behavior changed

Suggested format:

- Date (UTC)
- Change type (`feat`, `fix`, `docs`, `ci`, `refactor`)
- What changed
- Why it matters for users/CI
- Any migration note (if command behavior changed)

## License and Ownership

This project is licensed under the MIT License. See `LICENSE` for full text.

## Contributing

Contribution process and validation expectations are documented in `CONTRIBUTING.md`.

## Issue Reporting

Use the repository issue templates for consistent triage:

- Bug reports: `.github/ISSUE_TEMPLATE/bug_report.md`
- Feature requests: `.github/ISSUE_TEMPLATE/feature_request.md`
