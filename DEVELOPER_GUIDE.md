# Developer Guide

## Purpose

This guide explains how to extend the AI docs generator safely and consistently.

## Development Workflow

1. Implement logic in modular source files under src.
2. Add or update tests in tests for behavior changes.
3. Regenerate bootstrap using setup-ai-docs.py after generator/runtime changes.
4. Run the full test suite before committing.

## Add New Generator Functions

### Where to add code

- Shared docs generation: src/generators/core.py
- Compliance docs generation: src/generators/compliance.py
- Orchestration logic: setup-ai-docs.py generate_files flow

### Steps

1. Add a pure generator function that returns markdown content as a string.
2. Keep input shape based on ctx or explicit function args.
3. Export the function in src/generators/**init**.py.
4. Wire the function into generation flow where needed.
5. Add focused unit tests in tests/test_core_generators.py or tests/test_compliance_generators.py.

### Guidelines

- Keep functions deterministic for stable check mode behavior.
- Avoid side effects in generator functions.
- Use clear section headings in generated markdown.

## Add New Compliance Frameworks

### Where to add code

- Framework metadata and aliases: src/constants/compliance.py
- Level 2 scanning docs: src/generators/compliance.py in generate_level_2_compliance_scanning
- Level 3 implementation patterns: src/generators/compliance.py in generate_level_3_compliance_patterns

### Steps

1. Add framework entry to COMPLIANCE_PACKS with:
   - name
   - trigger_keywords
   - checks
2. Add alias mappings in COMPLIANCE_ALIASES.
3. Add Level 2 scanning template logic.
4. Add Level 3 patterns template logic if required.
5. Add tests that validate:
   - file generation
   - key checklist content
   - remediation or pattern sections

### Validation checklist

- Framework appears in list-compliance output.
- Framework resolves from aliases and intent keywords.
- Generated files are included for configured compliance level.

## Extend Stack Detection

### Where to add code

- Core detection logic: src/lib.py in detect_stack
- Stack preset catalog: src/constants/presets.py
- Framework intent bonus mapping: src/constants/hints.py
- Package guidance and audits: src/constants/hints.py

### Steps

1. Add manifest detection in detect_stack.
2. Map dependencies to framework names.
3. Add package manager identifier if needed.
4. Add framework-specific package guidance profile.
5. Add intent bonus hints for better blueprint ranking.
6. Add or update tests that cover detection and guidance output.

## Testing Commands

Run from repository root.

```bash
/opt/homebrew/bin/python3 -m unittest discover -s tests -v
```

Targeted tests:

```bash
/opt/homebrew/bin/python3 -m unittest tests.test_core_generators -v
/opt/homebrew/bin/python3 -m unittest tests.test_compliance_generators -v
/opt/homebrew/bin/python3 -m unittest tests.test_bootstrap_integration -v
```

## Bootstrap Regeneration

After modifying runtime-relevant logic, regenerate bootstrap.

```bash
/opt/homebrew/bin/python3 setup-ai-docs.py
```

Then re-run tests and verify output consistency.

## Common Pitfalls

- Forgetting to export new functions in package **init**.py files.
- Updating source generators without regenerating ai-docs-bootstrap.
- Adding non-deterministic content that breaks check-mode comparisons.
- Introducing alias keys without corresponding compliance pack entries.
