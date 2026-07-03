# Coding Agent - Next Steps TODO

## Phase 1: Code Consolidation

- [x] **Consolidate file utilities** - Merge `src/utils/file_ops.py` and `src/utils/file_io.py` into single module
  - Review overlapping functions
  - Create unified API
  - Update imports across codebase
- [x] **Remove redundant imports** - Clean up unused imports in setup-ai-docs.py
  - Audit all import statements
  - Remove unused dependencies
  - Organize imports by category

## Phase 2: Level 3 Compliance Implementation

- [x] **Implement PCI-DSS code patterns**
  - Payment handling examples
  - Encryption patterns
  - Access control templates
- [x] **Implement HIPAA code patterns**
  - PHI protection examples
  - Audit logging patterns
  - Encryption requirements
- [x] **Implement GDPR code patterns**
  - Data minimization patterns
  - Consent management examples
  - Right to deletion templates
- [x] **Implement SOC2 code patterns**
  - Security control examples
  - Access logging patterns
  - Change management templates
- [x] **Implement CCPA/CPRA code patterns**
  - Consumer rights examples
  - Opt-out mechanisms
  - Data deletion patterns
- [x] **Implement ISO27001 code patterns**
  - Security controls examples
  - Risk management templates
  - Incident response patterns

## Phase 3: Testing & Validation

- [x] **Create unit tests** for generator functions
  - [x] Test `src/generators/core.py`
  - [x] Test `src/generators/compliance.py`
  - [x] Test `src/utils/file_io.py`
- [x] **Create integration tests** for bootstrap execution
  - [x] Test with different compliance framework combinations
  - [x] Test with different OS targets
  - [x] Test feature spec generation
- [x] **Create compliance scanning validation tests**
  - [x] Verify all 6 frameworks generate scanning rules
  - [x] Validate compliance checklist content
  - [x] Test remediation guidance

- [x] **Performance benchmarks**
  - [x] Measure bootstrap generation time
  - [x] Profile code embedding performance
  - [x] Optimize hot paths

## Phase 4: Documentation

- [x] **Architecture documentation**
  - Document modularized structure
  - Explain function responsibilities
  - Create module dependency diagram
- [x] **Developer guide**
  - How to add new generator functions
  - How to add new compliance frameworks
  - How to extend stack detection
- [x] **API reference**
  - Document all public functions
  - Include parameter descriptions
  - Add usage examples
- [x] **Bootstrap deployment guide**
  - How to distribute ai-docs-bootstrap
  - Installation instructions
  - Configuration reference

## Phase 5: Feature Expansion

- [x] **Add new stack presets**
  - [x] Identify gaps in current 22 presets
  - [x] Add 5-10 new framework combinations
  - [x] Update constants in `src/constants.py`
- [x] **Add new app archetypes**
  - [x] Expand beyond 24 existing archetypes
  - [x] Add 5-10 new business patterns
  - [x] Update archetype detection logic
- [x] **Implement custom agent support**
  - [x] Allow users to define custom frameworks
  - [x] Custom compliance rules configuration
  - [x] Custom feature templates
- [x] **Add multi-language support**
  - Translate compliance scanning rules
  - Localize feature names
  - Regional compliance framework variants

## Phase 6: Advanced Features

- [x] **Implement Level 3 compliance code pattern injection**
  - [x] Analyze project code for pattern matching
  - [x] Suggest remediation code snippets
  - [x] Auto-patch vulnerable patterns
- [x] **Add AI-assisted compliance analysis**
  - [x] Use LLM to detect compliance risks
  - [x] Generate compliance reports
  - [x] Suggest architecture changes
- [x] **Create web dashboard** (optional)
  - [x] Project compliance status visualization
  - [x] File generation progress tracking
  - [x] Real-time scanning results

## Phase 7: Production Readiness

- [x] **Production hardening & security gates**
  - [x] Add strict input validation for custom config and CLI params
  - [x] Add safe limits/timeouts for file scanning and patch routines
  - [x] Add denylist/allowlist controls for patch-apply scope
- [x] **CI/CD compliance quality gates**
  - [x] Add GitHub Actions workflow for generator + tests + lint
  - [x] Add required check mode to fail on stale generated docs
  - [x] Publish compliance artifacts as CI build outputs
- [x] **CLI UX & release packaging**
  - [x] Add `--dry-run` generation summary mode
  - [x] Add version banner/changelog command
  - [x] Package and document release process for bootstrap distribution
- [x] **Observability & telemetry**
  - [x] Add run metrics (files scanned, findings, patches proposed/applied)
  - [x] Add structured JSON run report output option
  - [x] Track generation performance regressions over time
- [x] **Operational docs & support playbooks**
  - [x] Troubleshooting guide for common generator failures
  - [x] Security review checklist for auto-patch usage
  - [x] Upgrade/migration notes between generator versions

## Phase 8: Modular Features Follow-up

- [x] **Matrix test automation in CI**
  - Add a CI job to run feature selection matrix tests on every PR
  - Publish matrix summary as an artifact for troubleshooting
  - Fail CI on unsupported-feature validation regressions
- [x] **Feature dependency guardrails**
  - Define optional feature dependencies (e.g., dashboard requires level 3 scan context)
  - Validate incompatible combinations with actionable error messages
  - Document dependency rules in README and CLI help
- [x] **Preset-based feature profiles**
  - Add simple profiles like `minimal`, `standard`, `compliance-heavy`
  - Allow profile + explicit overrides (`--enable-features` / `--disable-features`)
  - Emit selected profile in `.ai-docs/FEATURES.md`
- [x] **Per-feature generation metrics**
  - Track generated file counts by feature key
  - Add feature-level timings to JSON report output
  - Surface slowest features in performance history reporting
- [x] **Golden snapshot coverage for feature outputs**
  - Add snapshot fixtures for key feature combinations
  - Detect accidental content drift in generated docs/specs
  - Include snapshot diff hints in CI artifact output
- [x] **Feature config import/export**
  - Add `--features-config` JSON input for repeatable runs
  - Add `--write-features-config` to persist active feature sets
  - Validate schema and reject unknown keys with clear errors
- [x] **Feature lifecycle policy**
  - Define policy for experimental/deprecated feature flags
  - Add CLI labels for stable vs experimental features
  - Document migration path when a feature is renamed/removed
- [x] **Matrix performance scaling**
  - Split matrix cases into fast and full tiers
  - Run fast tier on PRs and full tier on main/nightly
  - Track matrix duration trend and optimize slowest cases

---

## Notes

- Start with Phase 1 (consolidation) for immediate cleanup
- Phase 2 (compliance patterns) adds the most business value
- Phase 3 (testing) ensures stability at scale
- Phase 4 (documentation) facilitates adoption
- Phase 5+ (expansion) adds new capabilities

**Last Updated**: 2026-06-30
**Modularization Commit**: a115f7c
