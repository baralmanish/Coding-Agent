# Refactoring Guide - Completing the Modularization

This guide shows exactly which functions from the original `setup-ai-docs.py` need to be extracted into the new module structure.

## Phase 1: Constants (✅ COMPLETE)

### ✅ src/constants/compliance.py

- `COMPLIANCE_PACKS` (lines ~652-710) → **Done**
- `COMPLIANCE_ALIASES` (lines ~711-724) → **Done**

### ✅ src/constants/hints.py

- `FRAMEWORK_INTENT_HINTS` (lines ~725-733) → **Done**
- `PACKAGE_GUIDANCE` (lines ~734-774) → **Done**
- `SECURITY_AUDIT_COMMANDS` (lines ~775-814) → **Done**

### ✅ src/constants/presets.py

- `APP_ARCHETYPES` (lines ~273-438) → **Done**
- `INTENT_KEYWORD_BLUEPRINTS` (lines ~439-651) → **Done**

---

## Phase 2: Core Functions (⏳ TODO)

### → src/core/context.py

**From original setup-ai-docs.py, extract these functions:**

- `detect_stack()` (lines ~896-1024)
- `build_common_context()` (lines ~1602-1635)
- `resolve_compliance_packs()` (lines ~1086-1108)
- `resolve_app_blueprint()` (lines ~1180-1264)
- `compute_framework_intent_bonus()` (lines ~1153-1164)

**File I/O functions → move to `src/utils/file_ops.py`:**

- `read_json_file()` (lines ~853-859)
- `gather_existing_markdown_context()` (lines ~1024-1052)
- `write_metadata()` (lines ~1906-1925)
- `parse_requirements_txt()` (lines ~860-871)
- `parse_toml_dependencies()` (lines ~872-895)

**Project detection → move to `src/core/context.py`:**

- `detect_project_type()` (lines ~833-852)

### → src/core/generation.py

**From original setup-ai-docs.py, extract:**

- `generate_files()` (lines ~2297-2910)
- `determine_impacted_files()` (referenced within generate_files)

---

## Phase 3: Generators (⏳ TODO)

### → src/generators/documentation.py

**Extract these functions:**

- `generate_app_blueprint_md()` (lines ~1700-1800)
- `generate_index_md()` (referenced in generate_files)

### → src/generators/compliance.py

**Extract these functions:**

- `generate_level_2_compliance_scanning()` (lines ~2137-2290)
- Prepare for Level 3: `generate_level_3_compliance_patterns()` (deferred)

---

## Phase 4: Bootstrap Builder (⏳ TODO)

### → src/bootstrap_builder.py

**Extract (currently monolithic):**

- `build_bootstrap_script()` (lines ~40-3024) - Consider:
  - Extract embedded constants to template variables
  - Extract embedded functions to separate bootstrap module
  - Or: Keep as-is but document clearly

**Helper function to move:**

- `ask_target_os()` (lines ~20-39) → Can stay with bootstrap_builder

---

## Phase 5: Utilities (⏳ TODO)

### → src/utils/text.py

**Extract text processing functions:**

- `slugify_intent_key()` (lines ~1068-1072)
- `merge_unique()` (lines ~1053-1067)
- `keyword_confidence_score()` (lines ~1165-1179)
- `parse_compliance_input()` (lines ~1073-1085)
- `now_utc()` (lines ~817-819)
- `hash_text()` (lines ~821-824)
- `current_script_sha256()` (lines ~825-832)
- `resolve_package_guidance()` (lines ~1109-1152)

---

## Refactoring Steps

### Step 1: Extract and Test One Module at a Time

1. Choose a module from Phase 2 (easiest first: text.py)
2. Extract functions to the module file
3. Update imports in the original setup-ai-docs.py
4. Run tests: `python3 -m py_compile src/utils/text.py`
5. Test the original script still works

### Step 2: Create Wrapper setup-ai-docs.py

After extracting all modules:

```python
# New setup-ai-docs.py (thin wrapper)
from src.bootstrap_builder import build_bootstrap_script, ask_target_os
from src.core.context import build_common_context
from pathlib import Path

def main() -> None:
    script_dir = Path(__file__).resolve().parent
    # ... implementation using imported functions

if __name__ == "__main__":
    main()
```

### Step 3: Verify and Test

```bash
# Test syntax
python3 -m py_compile setup-ai-docs.py
python3 -m py_compile -r src/

# Run actual tool
python3 setup-ai-docs.py  # Should generate ai-docs-bootstrap

# Test bootstrap
cd /tmp/test-project && /path/to/ai-docs-bootstrap --help
```

---

## Extraction Template

When extracting a function, use this template:

```python
# In new module file (e.g., src/utils/text.py)

def function_name(arg1: str, arg2: dict) -> str:
    """Docstring explaining what the function does.

    Args:
        arg1: Description
        arg2: Description

    Returns:
        Description of return value
    """
    # [Copy function body from original setup-ai-docs.py]
    # Remember to import any dependencies it uses
    pass
```

Then update the original setup-ai-docs.py:

```python
# At the top of setup-ai-docs.py, add:
from src.utils.text import function_name

# Remove the old function definition
# All calls to function_name() remain unchanged
```

---

## Benefits Upon Completion

✅ Setup-ai-docs.py reduced from 3000+ lines to ~200 lines  
✅ Each module is independently testable  
✅ Debugging specific features requires finding code in right module, not scrolling through massive file  
✅ New features (Level 3 patterns, new compliance packs) easy to add  
✅ Bootstrap builder can be refactored separately without affecting main logic  
✅ Foundation for CI/CD enhancements and better testing

---

## Current Status

- Phase 1: ✅ COMPLETE - Constants extracted
- Phase 2: ⏳ TODO (10-15 mins work)
- Phase 3: ⏳ TODO (10-15 mins work)
- Phase 4: ⏳ TODO (optional: can refactor separately)
- Phase 5: ⏳ TODO (5-10 mins work)

**Next priority:** Phase 2 - Start with `src/utils/text.py` extraction
