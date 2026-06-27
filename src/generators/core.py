"""Core file generators for AI documentation files.

This module contains functions to generate agent-specific and shared
markdown documentation files based on project context and compliance settings.

Functions:
- generate_agents_md() - Generate cross-agent canonical guide
- generate_app_blueprint_md() - Generate application blueprint
- generate_index_md() - Generate documentation index
- generate_context_snapshot() - Generate project context snapshot
- generate_agent_specific_docs() - Generate agent-specific files
"""


def generate_agents_md(ctx: dict) -> str:
    """Generate AGENTS.md - cross-agent canonical guidance."""
    stack = ctx["stack"]
    langs = ", ".join(stack.get("languages") or ["TBD"])
    fws = ", ".join(stack.get("frameworks") or ["TBD"])
    app_label = ctx.get("app_blueprint", {}).get("label", "General App")
    app_desc = ctx.get("app_blueprint", {}).get(
        "description", "Balanced defaults for software delivery."
    )
    app_input = ctx.get("app_intent_input", ctx.get("app_intent", "general-app"))

    return f"""# AGENTS.md

Last updated: {ctx["generated_at"]}

## Purpose
Canonical cross-agent guidance for AI-assisted development in this repository.

## Project Context
- Project type: {ctx["project_type"]}
- Target OS: {ctx["target_os"]}
- App intent: {app_input} (profile: {ctx["app_intent"]} / {app_label})
- Languages: {langs}
- Frameworks: {fws}

## Product Intent
{app_desc}

## Core Engineering Rules
1. Preserve existing architecture and coding style unless change is requested.
2. Write or update tests for behavior changes.
3. Prefer small, reviewable diffs.
4. Avoid exposing secrets in code, docs, or logs.
5. Document assumptions and unknowns explicitly.

## Quality Gate
- Build passes
- Lint passes
- Tests pass
- Docs updated for behavior/interface changes

## Security Gate
- No embedded credentials or tokens
- Validate inputs at boundaries
- Apply least-privilege defaults

## Spec-Driven Development
Use docs as executable intent:
- Requirements and acceptance criteria first
- Tests mapped to acceptance criteria
- Implementation follows validated tests

## Token/Context Efficiency
- Read only necessary files first, then expand.
- Summarize large contexts before synthesis.
- Reuse canonical rules from this file in agent-specific docs.

## Update Policy
- Refresh docs when stack/tooling changes.
- Record updates in .ai-docs/CHANGELOG.md.
"""


def generate_app_blueprint_md(ctx: dict) -> str:
    """Generate APP-BLUEPRINT.md - application capabilities and suggestions."""
    blueprint = ctx.get("app_blueprint", {})
    capabilities = blueprint.get("capabilities", [])
    suggestions = blueprint.get("suggestions", [])
    compliance_packs = ctx.get("compliance_packs", [])
    package_guidance = ctx.get("package_guidance", {})
    intent_ranking = blueprint.get("intent_ranking", [])

    capabilities_lines = (
        "\n".join(f"- {item}" for item in capabilities)
        if capabilities
        else "- No capabilities defined"
    )
    suggestions_lines = (
        "\n".join(f"- {item}" for item in suggestions)
        if suggestions
        else "- No suggestions defined"
    )

    if compliance_packs:
        compliance_lines = []
        for pack in compliance_packs:
            compliance_lines.append(
                f"- {pack.get('name', pack.get('key', 'Unknown'))} ({pack.get('key', 'n/a')})"
            )
            for check in pack.get("checks", []):
                compliance_lines.append(f"  - {check}")
        compliance_text = "\n".join(compliance_lines)
    else:
        compliance_text = "- No specific compliance pack selected or auto-detected."

    if intent_ranking:
        ranking_lines = []
        for row in intent_ranking:
            keywords = ", ".join(row.get("matched_keywords", [])) or "n/a"
            base_score = row.get("base_score", row.get("score", 0))
            framework_bonus = row.get("framework_bonus", 0)
            ranking_lines.append(
                f"- {row.get('label', 'Unknown')}: score={row.get('score', 0)} (base={base_score}, framework_bonus={framework_bonus}, matched: {keywords})"
            )
        ranking_text = "\n".join(ranking_lines)
    else:
        ranking_text = "- No ranked intent matches; using default/general profile."

    recommended_packages = package_guidance.get("recommended_packages", [])
    avoid_packages = package_guidance.get("avoid_packages", [])
    audit_commands = package_guidance.get("audit_commands", [])

    recommended_text = (
        "\n".join(f"- {item}" for item in recommended_packages)
        if recommended_packages
        else "- No package recommendations available."
    )
    avoid_text = (
        "\n".join(f"- {item}" for item in avoid_packages)
        if avoid_packages
        else "- No stale package warnings available."
    )
    audit_text = (
        "\n".join(f"- `{item}`" for item in audit_commands)
        if audit_commands
        else "- No audit command recommendations available."
    )

    return f"""# Application Blueprint

Last updated: {ctx["generated_at"]}

## Selected Intent
- Key: {ctx.get("app_intent", "general-app")}
- Input: {ctx.get("app_intent_input", ctx.get("app_intent", "general-app"))}
- Label: {blueprint.get("label", "General App")}
- Description: {blueprint.get("description", "Balanced defaults for software delivery.")}

## Intent Ranking
{ranking_text}

## Capability Checklist
{capabilities_lines}

## Delivery Suggestions
{suggestions_lines}

## Compliance Packs
{compliance_text}

## Package Recommendations (Current Standard)
{recommended_text}

## Avoid Stale Packages
{avoid_text}

## Security Audit Before Install
1. Run vulnerability and advisory checks before adding new dependencies.
2. Prefer actively maintained libraries with regular releases and security response history.
3. Block install/merge when high or critical issues are unresolved.

Suggested commands:
{audit_text}

## Stack-Specific Notes
- React/Next: prioritize typed API clients, optimistic UI boundaries, and role-aware routes.
- Node/Nest/Fastify: isolate domain services from transport; enforce request/schema validation.
- Laravel: use policies, form requests, queues, and database transactions for critical flows.
- Python (FastAPI/Django): validate contracts with pydantic/dataclasses and secure async/background tasks.

## Spec-Driven Development
This project supports advanced development workflows:
- **Executable Specs**: Turn requirements into validated specifications (see `.ai-docs/EXECUTABLE-SPECS.md`)
- **Code Validation**: Validate correctness beyond unit tests (see `.ai-docs/CODE-VALIDATION.md`)
- **Parallel Agents**: Coordinate multiple agents with session-based learning (see `.ai-docs/PARALLEL-AGENTS.md`)

Recommended approach:
1. Define executable specs in `.specs/` folder with acceptance criteria and assertions.
2. Implement code to satisfy assertions (faster than iterative fixing).
3. Run validation suite to find bugs unit tests miss.
4. Coordinate work across agents using shared specs and session memory.

## Memory Management Strategy
Use the three-layer memory approach (key-value store + selective graph + session memory) to minimize LLM calls:
- Track only what changed each session (3-5 LLM calls vs 20+ for full re-extraction)
- Use key-value pairs for fast fact lookup
- Update selective graph edges only when relationships change
- Record session memory for continuous improvement

See `.ai-docs/MEMORY-MANAGEMENT.md` for full details.
"""


def generate_index_md(ctx: dict, files: list[str]) -> str:
    """Generate AI_DOCS_INDEX.md - navigation and overview."""
    files_section = (
        "\n".join(f"- {f}" for f in sorted(files)) if files else "- (none yet)"
    )

    return f"""# AI Docs Index

Last generated: {ctx["generated_at"]}
Project type: {ctx["project_type"]}
Target OS: {ctx["target_os"]}

## Quick Navigation

### Core Guidance
- `AGENTS.md` - Cross-agent canonical guide and quality gates.
- `APP-BLUEPRINT.md` - Application capabilities, compliance, and stack recommendations.
- `.ai-docs/CONTEXT-SNAPSHOT.md` - Detected project context summary.

### Reference
- `.ai-docs/MASTER_PROMPT_REFERENCE.md` - Master prompt used to generate this documentation.
- `.ai-docs/CHANGELOG.md` - Documentation change history.
- `.ai-docs/FEEDBACK.md` - Feedback and improvement process.

### Advanced Features
- `.ai-docs/EXECUTABLE-SPECS.md` - Spec-driven development guide.
- `.ai-docs/CODE-GENERATION-STANDARDS.md` - Code patterns and standards.
- `.ai-docs/CODE-VALIDATION.md` - Beyond unit tests: integrated validation.
- `.ai-docs/MEMORY-MANAGEMENT.md` - Session and context memory strategy.
- `.ai-docs/TOKEN-EFFICIENCY.md` - Minimize prompt size while preserving signal.
- `.ai-docs/PARALLEL-AGENTS.md` - Multi-agent coordination and handoff.
- `.ai-docs/KNOWLEDGE-VAULT.md` - Centralized facts, decision logs, and terminology.

### Agent-Specific Rules
- `.cursor/rules/project.mdc` - Cursor-specific configuration.
- `.github/copilot-instructions.md` - GitHub Copilot instructions.
- `CLAUDE.md` - Claude Code agent guidance.

### Specifications
- `.specs/` - Feature specs, compliance scanning rules, and validation scripts.

## Managed Files
{files_section}

## File Update Policy
- Edit `.ai-docs/*` files directly.
- Mark user customizations with `<!-- user-custom:start -->` and `<!-- user-custom:end -->` comments.
- Re-run `ai-docs-bootstrap` to refresh generated sections while preserving customizations.

## Feedback & Improvements
File improvement requests in `.ai-docs/FEEDBACK.md` with:
- File and section affected
- Current vs. desired outcome
- Context (link to code, decision, or test)
"""


def generate_context_snapshot(ctx: dict, markdown_context: list[dict]) -> str:
    """Generate CONTEXT-SNAPSHOT.md - detected project context."""
    stack = ctx["stack"]

    languages = ", ".join(stack.get("languages") or ["(not detected)"])
    frameworks = ", ".join(stack.get("frameworks") or ["(not detected)"])
    package_managers = ", ".join(stack.get("package_managers") or ["(not detected)"])
    packages = ", ".join(stack.get("packages") or ["(not detected)"])

    existing_docs = (
        "\n".join(f"- {d['path']}: {d['preview'][:100]}..." for d in markdown_context)
        if markdown_context
        else "- (none found)"
    )

    return f"""# Context Snapshot

Captured at: {ctx["generated_at"]}

## Project Type
{ctx["project_type"]}

## Stack Detection
- **Languages**: {languages}
- **Frameworks**: {frameworks}
- **Package Managers**: {package_managers}
- **Packages**: {packages}

## Detected Context
- **App Intent**: {ctx.get("app_intent", "general-app")} ({ctx.get("app_intent_input", "n/a")})
- **Target OS**: {ctx["target_os"]}
- **Compliance Level**: {ctx.get("compliance_level", 0)}
- **Compliance Keys**: {", ".join(p.get("key", "unknown") for p in ctx.get("compliance_packs", [])) or "(none)"}
- **Enabled Agents**: {", ".join(ctx.get("agents", [])) or "(none)"}

## Existing Markdown Docs
{existing_docs}

## Next Steps
1. Review `APP-BLUEPRINT.md` for capability checklist and recommendations.
2. Review agent-specific files (`.cursor/rules/project.mdc`, `.github/copilot-instructions.md`, etc.).
3. Update `.ai-docs/FEEDBACK.md` with any missing guidance or corrections.
4. Commit changes: `git add .ai-docs/ .cursor/ .github/copilot-instructions.md && git commit -m "docs: initialize AI agent documentation"`
"""


def generate_agent_specific_docs(ctx: dict) -> dict[str, str]:
    """Generate agent-specific documentation files."""
    docs = {}

    # Cursor rules
    docs[".cursor/rules/project.mdc"] = f"""# Cursor Configuration for This Project

Generated: {ctx["generated_at"]}

## Core Rules
- Follow patterns in existing code.
- Ask before making major architectural changes.
- Preserve test coverage when refactoring.
- Use git history to understand intent.

## Stack Context
- Languages: {", ".join(ctx["stack"].get("languages", []) or ["TBD"])}
- Frameworks: {", ".join(ctx["stack"].get("frameworks", []) or ["TBD"])}

## Quality Requirements
- Lint passes.
- Tests pass.
- No security warnings.

## Reference
See `AGENTS.md` for full guidance.
"""

    # GitHub Copilot instructions
    docs[".github/copilot-instructions.md"] = f"""# GitHub Copilot Instructions

Generated: {ctx["generated_at"]}

## Core Principles
- Preserve existing architecture and code style.
- Follow test-driven development (TDD) when adding features.
- Write small, focused commits with clear messages.
- Link commits to issues or pull request discussions.

## Stack
- Languages: {", ".join(ctx["stack"].get("languages", []) or ["TBD"])}
- Frameworks: {", ".join(ctx["stack"].get("frameworks", []) or ["TBD"])}
- Testing: {", ".join(ctx["stack"].get("scripts", {}).get("test", []) or ["run tests with available framework"])}

## Quality Checklist
✓ Lint passes (existing tool configuration)
✓ All tests pass
✓ No new security warnings
✓ Behavior documented in comments (if non-obvious)

## References
- See `AGENTS.md` for canonical guidance.
- See `.cursor/rules/project.mdc` for cursor-specific setup.
"""

    return docs
