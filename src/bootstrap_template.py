"""Template builder for generated ai-docs-bootstrap runtime script."""

from __future__ import annotations

import json

from src.bootstrap_builder import _prepare_embedded_sources
from src.bootstrap_template_runtime import render_bootstrap_runtime
from src.constants import (
    STACK_PRESETS,
    APP_ARCHETYPES,
    INTENT_KEYWORD_BLUEPRINTS,
)


def build_bootstrap_script(master_prompt: str, target_os: str) -> str:
    prompt_literal = json.dumps(master_prompt)
    target_os_literal = json.dumps(target_os)
    stack_presets_literal = json.dumps(STACK_PRESETS, indent=4)
    app_archetypes_literal = json.dumps(APP_ARCHETYPES, indent=4)
    intent_keyword_blueprints_literal = json.dumps(INTENT_KEYWORD_BLUEPRINTS, indent=4)
    utility_functions_escaped, gen_functions_escaped = _prepare_embedded_sources()

    gen_functions_setup = f"""# Embed utility functions
exec({utility_functions_escaped}, globals())
# Embed generator functions (core + compliance + file_io)
exec({gen_functions_escaped}, globals())"""

    return render_bootstrap_runtime(
        prompt_literal=prompt_literal,
        target_os_literal=target_os_literal,
        stack_presets_literal=stack_presets_literal,
        app_archetypes_literal=app_archetypes_literal,
        intent_keyword_blueprints_literal=intent_keyword_blueprints_literal,
        gen_functions_setup=gen_functions_setup,
    )
