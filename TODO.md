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

- [ ] **Architecture documentation**
  - Document modularized structure
  - Explain function responsibilities
  - Create module dependency diagram
- [ ] **Developer guide**
  - How to add new generator functions
  - How to add new compliance frameworks
  - How to extend stack detection
- [ ] **API reference**
  - Document all public functions
  - Include parameter descriptions
  - Add usage examples
- [ ] **Bootstrap deployment guide**
  - How to distribute ai-docs-bootstrap
  - Installation instructions
  - Configuration reference

## Phase 5: Feature Expansion

- [ ] **Add new stack presets**
  - Identify gaps in current 22 presets
  - Add 5-10 new framework combinations
  - Update constants in `src/constants.py`
- [ ] **Add new app archetypes**
  - Expand beyond 24 existing archetypes
  - Add 5-10 new business patterns
  - Update archetype detection logic
- [ ] **Implement custom agent support**
  - Allow users to define custom frameworks
  - Custom compliance rules configuration
  - Custom feature templates
- [ ] **Add multi-language support**
  - Translate compliance scanning rules
  - Localize feature names
  - Regional compliance framework variants

## Phase 6: Advanced Features

- [ ] **Implement Level 3 compliance code pattern injection**
  - Analyze project code for pattern matching
  - Suggest remediation code snippets
  - Auto-patch vulnerable patterns
- [ ] **Add AI-assisted compliance analysis**
  - Use LLM to detect compliance risks
  - Generate compliance reports
  - Suggest architecture changes
- [ ] **Create web dashboard** (optional)
  - Project compliance status visualization
  - File generation progress tracking
  - Real-time scanning results

---

## Notes

- Start with Phase 1 (consolidation) for immediate cleanup
- Phase 2 (compliance patterns) adds the most business value
- Phase 3 (testing) ensures stability at scale
- Phase 4 (documentation) facilitates adoption
- Phase 5+ (expansion) adds new capabilities

**Last Updated**: 2026-06-27
**Modularization Commit**: 859912d
