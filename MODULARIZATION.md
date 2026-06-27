# AI Docs Bootstrap - Modular Architecture

## Overview

This refactored structure organizes the `setup-ai-docs.py` into logical modules for better maintainability, debugging, and extensibility.

## Directory Structure

```
setup-ai-docs.py (entry point - wrapper)
src/
├── __init__.py
├── constants/
│   ├── __init__.py                    # Re-exports all constants
│   ├── compliance.py                  # COMPLIANCE_PACKS, COMPLIANCE_ALIASES
│   ├── hints.py                       # FRAMEWORK_INTENT_HINTS, PACKAGE_GUIDANCE, SECURITY_AUDIT_COMMANDS
│   └── presets.py                     # APP_ARCHETYPES, INTENT_KEYWORD_BLUEPRINTS, STACK_PRESETS
├── bootstrap_builder.py               # build_bootstrap_script() - generates ai-docs-bootstrap executable
├── core/
│   ├── __init__.py
│   ├── context.py                     # Context building and project detection
│   └── generation.py                  # File generation orchestration
├── generators/
│   ├── __init__.py
│   ├── compliance.py                  # generate_level_2_compliance_scanning()
│   ├── documentation.py               # generate_app_blueprint_md(), documentation generators
│   └── index.py                       # Index file generation
└── utils/
    ├── __init__.py
    ├── file_ops.py                    # File I/O utilities
    └── text.py                        # Text processing helpers
```

##Module Responsibilities

### Constants (`src/constants/`)

- **compliance.py**: Compliance framework definitions (PCI-DSS, HIPAA, SOC2, GDPR, CCPA, ISO27001)
- **hints.py**: Framework-specific hints and package recommendations
- **presets.py**: App archetypes and intent blueprints

### Bootstrap (`src/bootstrap_builder.py`)

- `build_bootstrap_script()`: Generates the complete ai-docs-bootstrap executable
- Note: This remains mostly intact as it embeds constants in a large f-string template

### Core (`src/core/`)

- **context.py**: Project detection, stack analysis, context building
- **generation.py**: Main orchestration for file generation and metadata handling

### Generators (`src/generators/`)

- **compliance.py**: Compliance file generation (Levels 1-2)
- **documentation.py**: Blueprint, specs, and documentation generation
- **index.py**: Index and manifest generation

### Utils (`src/utils/`)

- **file_ops.py**: File I/O, path handling, text preservation
- **text.py**: Text utilities, formatting, slugification

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a single, clear responsibility
2. **Easier Debugging**: Find relevant code quickly without scrolling through 3000 lines
3. **Testability**: Individual modules can be tested in isolation
4. **Extensibility**: Adding new compliance levels or generators is straightforward
5. **Level 3 Implementation**: Now feasible to add code patterns without f-string complexity

## Usage

```bash
# Generate bootstrap executable (unchanged)
python3 setup-ai-docs.py

# Use generated bootstrap (unchanged)
./ai-docs-bootstrap --help
```

## Implementation Timeline

Phase 1 (Completed):

- ✅ Created module structure with constants

Phase 2 (In Progress):

- Extract core utility functions
- Move bootstrap builder (with appropriate refactoring)
- Create generators modules

Phase 3 (Next):

- Refactor setup-ai-docs.py as thin wrapper
- Add tests for individual modules
- Implement Level 3 patterns (now easier without f-string limits)

## Next Steps for Development

1. **Extract remaining utility functions** into `core/` and `utils/`
2. **Move bootstrap builder** to its own module with template extraction
3. **Create test files** for each module in `tests/`
4. **Add Level 3 implementation** in `generators/compliance.py`
5. **Add CLI tests** and integration tests
