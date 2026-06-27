# Modularized Source Structure

This directory contains the modularized components of the AI docs generation system.

## Architecture

```
setup-ai-docs.py (CLI builder, ~3200 lines)
  ↓ imports
src/bootstrap_builder.py (build_bootstrap_script function)
  ↓ generates
ai-docs-bootstrap (2800-line self-contained executable)
```

## Modules

### `lib.py` (470 lines, 30+ functions)

Core utility functions for stack detection, compliance parsing, etc.

**Key Functions:**

- `detect_stack()` - Detect framework stack from package files
- `detect_project_type()` - Identify project mode (new/existing)
- `parse_compliance_input()` - Parse compliance arguments
- `resolve_compliance_packs()` - Map compliance levels to frameworks
- `keyword_confidence_score()` - Score compliance keyword matches
- And 25+ more utilities

**Note:** Missing functions that are still in setup-ai-docs.py:

- `resolve_app_blueprint()` - Resolve app intent to blueprint
- `resolve_package_guidance()` - Resolve package recommendations

### `constants/` (Directory)

All framework data, compliance frameworks, stack presets.

- `compliance.py` - 6 compliance frameworks (PCI-DSS, HIPAA, GDPR, SOC2, CCPA/CPRA, ISO27001)
- `hints.py` - 24 app archetypes with intent keywords and blueprints
- `presets.py` - 22 stack presets (React, Vue, Express, Django, FastAPI, etc.)
- `guidance.py` - Package recommendations and security audit commands

### `core/` (Directory)

Context building and metadata management (modular).

- `generation.py` - `build_common_context()` with injectable function pattern
- Used for building context dictionaries from project detection results

### `bootstrap_builder.py`

Wrapper function for bootstrap executable generation.

- `build_bootstrap_script(master_prompt, target_os) -> str`
- Returns 2800+ line self-contained executable Python script
- No external dependencies (all code embedded in f-string)

### `generators/` (Directory, stub)

Future location for file generation functions:

- `compliance_scanning.py` - Generate .specs/compliance/\*.md files
- `blueprints.py` - Generate APP-BLUEPRINT.md
- `indexes.py` - Generate AI_DOCS_INDEX.md

### `utils/` (Directory, stub)

Future location for utility functions:

- `files.py` - File I/O operations
- `text.py` - Text normalization and formatting
- `validation.py` - Input validation

## Design Principles

1. **Bootstrap is Self-Contained**: The generated bootstrap executable must have NO external imports. All code is embedded in an f-string.

2. **Thin Wrapper Pattern**: setup-ai-docs.py is a thin CLI wrapper that:
   - Reads master-prompt.md
   - Asks for target OS
   - Calls `build_bootstrap_script()`
   - Writes executable

3. **Modular Constants**: All framework data (compliance, stacks, archetypes) is centralized in `constants/` for easy updates.

4. **Injectable Functions**: Core context builders use injectable function parameters to avoid circular imports (e.g., `build_common_context(..., resolve_app_fn=None)`).

## Integration Status

- ✅ Constants modularized (COMPLIANCE_PACKS, STACK_PRESETS, etc.)
- ✅ Library functions modularized (detect_stack, detect_project_type, etc.)
- ✅ Bootstrap builder modularized
- ✅ Core context builder modularized (injectable)
- ⏳ File generators (compliance scanning) - next priority
- ⏳ setup-ai-docs.py full imports - lower priority (not necessary)

## Usage in setup-ai-docs.py

```python
from src.bootstrap_builder import build_bootstrap_script

# Generate bootstrap script
bootstrap_code = build_bootstrap_script(
    master_prompt=prompt_text,
    target_os="auto"
)

# Write to file
with open("ai-docs-bootstrap", "w") as f:
    f.write(bootstrap_code)
```

## Testing

```bash
# Test imports
python3 -c "from src.lib import detect_stack; from src.constants import COMPLIANCE_PACKS; print('✓ OK')"

# Generate bootstrap
python3 setup-ai-docs.py <<< "4\n\n\n\n\n\n\n\n1\n"

# Test bootstrap on project
./ai-docs-bootstrap --non-interactive --compliance pci-dss,hipaa --compliance-level 2
```
