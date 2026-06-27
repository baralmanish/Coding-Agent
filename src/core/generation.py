"""Core context building and metadata management."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.lib import (
    current_script_sha256,
    hash_text,
)


def now_utc() -> str:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def build_common_context(
    project_type: str,
    stack: dict,
    new_details: dict | None,
    generated_at: str,
    resolve_app_fn=None,
    resolve_compliance_fn=None,
    resolve_guidance_fn=None,
) -> dict:
    """Build context for documentation generation.

    Args:
        project_type: Type of project (new/existing)
        stack: Stack detection results
        new_details: New project details from user
        generated_at: Generation timestamp
        resolve_app_fn: Function to resolve app blueprint (from setup-ai-docs.py)
        resolve_compliance_fn: Function to resolve compliance packs
        resolve_guidance_fn: Function to resolve package guidance
    """
    DEFAULT_AGENTS = [
        "cursor",
        "github-copilot",
        "claude-code",
        "openai-codex",
        "antigravity",
    ]
    GENERATOR_TARGET_OS = "auto"  # Default, can be overridden in CLI

    agents = list(DEFAULT_AGENTS)
    target_os = GENERATOR_TARGET_OS if GENERATOR_TARGET_OS != "auto" else "auto"
    app_intent_input = "general-app"
    compliance_keys = []
    compliance_level = 1

    if new_details:
        agents = new_details.get("agents") or agents
        target_os = new_details.get("target_os") or target_os
        app_intent_input = (
            new_details.get("app_intent_input")
            or new_details.get("app_intent")
            or app_intent_input
        )
        compliance_keys = new_details.get("compliance_keys") or []
        compliance_level = new_details.get("compliance_level", 1)

    # Use injected functions if provided, otherwise use stubs
    if resolve_app_fn:
        app_intent, app_intent_display, app_blueprint = resolve_app_fn(
            app_intent_input, stack
        )
    else:
        app_intent, app_intent_display = app_intent_input, app_intent_input
        app_blueprint = {
            "label": app_intent_input,
            "description": "",
            "capabilities": [],
            "suggestions": [],
        }

    if resolve_compliance_fn:
        compliance_packs = resolve_compliance_fn(app_intent_display, compliance_keys)
    else:
        compliance_packs = []

    if resolve_guidance_fn:
        package_guidance = resolve_guidance_fn(stack)
    else:
        package_guidance = {
            "matched_profiles": [],
            "recommended_packages": [],
            "avoid_packages": [],
            "audit_commands": [],
        }

    return {
        "project_type": project_type,
        "target_os": target_os,
        "app_intent": app_intent,
        "app_intent_input": app_intent_display,
        "app_blueprint": app_blueprint,
        "compliance_packs": compliance_packs,
        "compliance_level": compliance_level,
        "package_guidance": package_guidance,
        "agents": agents,
        "stack": stack,
        "new_details": new_details or {},
        "generated_at": generated_at,
    }


def load_previous_metadata(project_dir: Path) -> dict:
    """Load previous generation metadata."""
    metadata_path = project_dir / ".ai-docs" / "metadata.json"
    if not metadata_path.exists():
        return {}
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def list_signature(values: list[str] | None) -> list[str]:
    """Sort list for comparison."""
    return sorted((values or []), key=lambda item: item.lower())


def detect_scope_changes(
    previous: dict, ctx: dict, master_prompt: str
) -> tuple[bool, bool, bool]:
    """Detect if generation scope changed."""
    old_stack = previous.get("stack", {})
    new_stack = ctx.get("stack", {})
    stack_changed = any(
        list_signature(old_stack.get(key)) != list_signature(new_stack.get(key))
        for key in ["languages", "frameworks", "package_managers"]
    )

    agents_changed = list_signature(previous.get("agents")) != list_signature(
        ctx.get("agents")
    )
    prompt_changed = previous.get("master_prompt_sha256") != hash_text(master_prompt)
    script_changed = previous.get("script_sha256") != current_script_sha256()
    old_intent = (previous.get("app_intent") or "").strip().lower()
    new_intent = (ctx.get("app_intent") or "").strip().lower()

    old_compliance = sorted(previous.get("compliance_keys", []) or [])
    new_compliance = sorted(
        [
            pack.get("key")
            for pack in (ctx.get("compliance_packs", []) or [])
            if pack.get("key")
        ]
    )

    profile_changed = (old_intent != new_intent) or (old_compliance != new_compliance)
    return (
        stack_changed,
        agents_changed,
        (prompt_changed or profile_changed or script_changed),
    )


def determine_impacted_files(
    project_dir: Path,
    ctx: dict,
    all_files: dict[str, str],
    agent_files: dict[str, str],
    check_mode: bool,
    master_prompt: str,
) -> tuple[set[str], bool, bool, bool]:
    """Determine which files need regeneration."""
    if check_mode:
        return set(all_files.keys()), True, True, True

    previous = load_previous_metadata(project_dir)
    if not previous:
        return set(all_files.keys()), True, True, True

    stack_changed, agents_changed, prompt_changed = detect_scope_changes(
        previous, ctx, master_prompt
    )
    impacted = {".ai-docs/CONTEXT-SNAPSHOT.md"}

    if stack_changed:
        impacted = set(all_files.keys())
    else:
        if agents_changed:
            impacted.update(agent_files.keys())
            impacted.update({"AGENTS.md", "AI_DOCS_INDEX.md"})
        if prompt_changed:
            impacted.add(".ai-docs/MASTER_PROMPT_REFERENCE.md")

    return impacted, stack_changed, agents_changed, prompt_changed


def write_metadata(
    project_dir: Path, ctx: dict, generated_files: list[str], master_prompt: str
) -> None:
    """Write generation metadata to disk."""
    GENERATOR_VERSION = "1.0.0"
    metadata_path = project_dir / ".ai-docs" / "metadata.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generator_version": GENERATOR_VERSION,
        "generated_at": ctx["generated_at"],
        "target_os": ctx["target_os"],
        "project_type": ctx["project_type"],
        "app_intent": ctx.get("app_intent"),
        "app_intent_input": ctx.get("app_intent_input"),
        "compliance_keys": [
            pack.get("key")
            for pack in (ctx.get("compliance_packs", []) or [])
            if pack.get("key")
        ],
        "compliance_level": ctx.get("compliance_level", 1),
        "agents": ctx["agents"],
        "stack": ctx["stack"],
        "master_prompt_sha256": hash_text(master_prompt),
        "script_sha256": current_script_sha256(),
        "generated_files": generated_files,
    }
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
