"""Runtime template rendering for ai-docs-bootstrap."""

from __future__ import annotations

from src.bootstrap_template_runtime_cli import render_runtime_cli
from src.bootstrap_template_runtime_main import render_runtime_main
from src.bootstrap_template_runtime_prelude import render_runtime_prelude


def render_bootstrap_runtime(
    prompt_literal: str,
    target_os_literal: str,
    stack_presets_literal: str,
    app_archetypes_literal: str,
    intent_keyword_blueprints_literal: str,
    gen_functions_setup: str,
) -> str:
    return (
        render_runtime_prelude(
            prompt_literal=prompt_literal,
            target_os_literal=target_os_literal,
            stack_presets_literal=stack_presets_literal,
            app_archetypes_literal=app_archetypes_literal,
            intent_keyword_blueprints_literal=intent_keyword_blueprints_literal,
            gen_functions_setup=gen_functions_setup,
        )
        + render_runtime_cli()
        + render_runtime_main()
    )
