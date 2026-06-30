# API Reference

## Purpose

This reference covers public module surfaces used by the builder and bootstrap runtime.

## Generators API

Module: src/generators

### generate_agents_md(ctx)

- Input: context dictionary
- Output: AGENTS markdown string
- Responsibility: shared cross-agent guidance

### generate_app_blueprint_md(ctx)

- Input: context dictionary
- Output: APP-BLUEPRINT markdown string
- Responsibility: app intent, compliance, and package guidance summary

### generate_index_md(ctx, files)

- Input: context dictionary and list of managed file paths
- Output: AI_DOCS_INDEX markdown string
- Responsibility: navigation and managed files index

### generate_context_snapshot(ctx, markdown_context)

- Input: context dictionary and discovered markdown context list
- Output: CONTEXT-SNAPSHOT markdown string
- Responsibility: stack and environment snapshot

### generate_agent_specific_docs(ctx)

- Input: context dictionary
- Output: mapping of relative path to markdown content
- Responsibility: agent-specific docs such as Cursor and Copilot instruction files

### generate_level_2_compliance_scanning(compliance_packs)

- Input: list of resolved compliance pack dictionaries
- Output: mapping of scanning file paths to markdown content
- Responsibility: Level 2 scanning and validation guidance docs

### generate_level_3_compliance_patterns(compliance_packs)

- Input: list of resolved compliance pack dictionaries
- Output: mapping of pattern file paths to markdown content
- Responsibility: Level 3 implementation examples and acceptance criteria

## Utility API

Module: src/utils/file_io.py

### ensure_dir(path)

- Creates directory tree if missing.

### write_text(path, content)

- Writes normalized content with trailing newline.

### read_text_if_exists(path)

- Returns file text or empty string when unavailable.

### normalize_text(content)

- Normalizes trailing whitespace/newline for deterministic comparisons.

### append_changelog(changelog_path, summary, now_utc_fn=None)

- Appends changelog entry with timestamp.
- Supports timestamp function injection for tests.

### load_previous_metadata(project_dir)

- Reads generation metadata from .ai-docs/metadata.json.

### read_json_file(path)

- Reads JSON safely and returns empty mapping on failures.

### write_metadata(project_dir, metadata)

- Writes metadata JSON under .ai-docs.

### gather_existing_markdown_context(project_dir, max_files=20)

- Scans non-generated markdown files for context previews.

## Core Generation API

Module: src/core/generation.py

### build_common_context(project_type, stack, new_details, generated_at)

- Builds normalized context consumed by generator functions.

### determine_impacted_files(project_dir, ctx, all_files, agent_files, check_mode, master_prompt)

- Calculates impacted files for selective regeneration.

### write_metadata(project_dir, ctx, generated_files, master_prompt)

- Persists metadata including stack, compliance keys, and hashes.

## Lib API Highlights

Module: src/lib.py

### detect_project_type(project_dir)

- Returns project mode classification for new versus existing repositories.

### detect_stack(project_dir)

- Detects languages, frameworks, package managers, packages, and scripts.

### parse_compliance_input(raw)

- Parses compliance key input with alias handling.

### resolve_compliance_packs(app_intent_input, selected_keys=None)

- Resolves explicit and intent-triggered compliance packs.

### resolve_package_guidance(stack)

- Returns recommended packages, avoid list, and security audit commands.

### resolve_app_blueprint(raw_intent, stack)

- Ranks intent profiles and returns selected blueprint.

## Builder API

Module: setup-ai-docs.py

### build_bootstrap_script(master_prompt, target_os)

- Produces standalone bootstrap script text.

### main()

- Builder entrypoint that writes ai-docs-bootstrap.

## Stability Notes

- Function signatures listed here are current stable surfaces used internally.
- Keep backward compatibility for bootstrap-facing behavior unless versioning changes are planned.
