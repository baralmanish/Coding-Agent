"""Main execution template section for ai-docs-bootstrap."""

from __future__ import annotations


def render_runtime_main() -> str:
    return f'''\

def main() -> None:
    args = parse_args()

    if args.version:
        print(f"ai-docs-bootstrap generator version: {{GENERATOR_VERSION}}")
        print("Recent release highlights:")
        print("- Phase 5: presets, archetypes, custom agent config, localization")
        print("- Phase 6: analysis, patch proposals/apply, dashboard")
        print("- Phase 7: hardening and CI quality gates")
        raise SystemExit(0)

    if args.list_stack_presets or args.list_intents or args.list_compliance:
        print_catalogs(args.list_stack_presets, args.list_intents, args.list_compliance)
        raise SystemExit(0)

    if args.list_feature_profiles:
        print("Available feature profiles:")
        for name, features in FEATURE_PROFILES.items():
            print(f"- {{name}}: {{', '.join(features)}}")
        print(f"\\nDefault profile mapping: {{default_feature_profile_name()}}")
        raise SystemExit(0)

    if args.list_features:
        print("Available feature options:")
        for name, description in FEATURE_CATALOG.items():
            lifecycle = get_feature_lifecycle(name)
            requirements = []
            if name in FEATURE_DEPENDENCIES:
                requirements.extend(FEATURE_DEPENDENCIES[name])
            if name == "auto-patch-apply":
                requirements.append("--apply-auto-patches")
            suffix_parts = [f"{{lifecycle['status']}}"]
            if requirements:
                suffix_parts.append(f"requires: {{', '.join(requirements)}}")
            if lifecycle["note"]:
                suffix_parts.append(lifecycle["note"])
            suffix = f" ({{'; '.join(suffix_parts)}})"
            print(f"- {{name}}: {{description}}{{suffix}}")
        if FEATURE_RENAMES:
            print("\\nFeature rename aliases (auto-migrated):")
            for old_name, new_name in sorted(FEATURE_RENAMES.items()):
                print(f"- {{old_name}} -> {{new_name}}")
        if FEATURE_REMOVED:
            print("\\nRemoved feature keys (migration guidance):")
            for removed_name, guidance in sorted(FEATURE_REMOVED.items()):
                print(f"- {{removed_name}}: {{guidance}}")
        print("\\nDefault active features:")
        for name in default_active_features():
            print(f"- {{name}}")
        raise SystemExit(0)

    project_dir = Path(args.project).resolve()
    if not project_dir.exists() or not project_dir.is_dir():
        raise SystemExit(f"Project path does not exist or is not a directory: {{project_dir}}")

    detected = detect_project_type(project_dir)
    mode = args.mode if args.mode != "auto" else detected

    if args.mode == "auto":
        print(f"Detected project mode: {{detected}}")
    else:
        print(f"Using override mode: {{mode}}")

    stack = detect_stack(project_dir)
    context_max_files = int(max(1, min(args.context_max_files, 200)))
    context_preview_chars = int(max(100, min(args.context_preview_chars, 8000)))
    try:
        markdown_context = gather_existing_markdown_context(
            project_dir,
            max_files=context_max_files,
            preview_chars=context_preview_chars,
        )
    except TypeError:
        # Backward-compatible fallback when embedded helper only supports max_files.
        markdown_context = gather_existing_markdown_context(project_dir, context_max_files)
        for item in markdown_context:
            if isinstance(item, dict):
                item["preview"] = str(item.get("preview", ""))[:context_preview_chars]

    try:
        imported_feature_config = load_feature_config((args.features_config or "").strip())
    except ValueError as exc:
        raise SystemExit(str(exc))

    explicit_features = list(imported_feature_config.get("features", []))
    enable_features = list(imported_feature_config.get("enable_features", []))
    disable_features = list(imported_feature_config.get("disable_features", []))

    cli_explicit_features = parse_csv_items(args.features or "")
    if cli_explicit_features:
        explicit_features = cli_explicit_features

    cli_enable_features = parse_csv_items(args.enable_features or "")
    if cli_enable_features:
        enable_features = merge_unique(enable_features, cli_enable_features)

    cli_disable_features = parse_csv_items(args.disable_features or "")
    if cli_disable_features:
        disable_features = merge_unique(disable_features, cli_disable_features)

    selected_feature_profile = None
    selected_feature_profile_raw = args.feature_profile or imported_feature_config.get("feature_profile")
    if selected_feature_profile_raw:
        try:
            selected_feature_profile, _ = resolve_feature_profile(selected_feature_profile_raw)
        except ValueError as exc:
            raise SystemExit(str(exc))

    apply_auto_patches = bool(args.apply_auto_patches) or bool(
        imported_feature_config.get("apply_auto_patches", False)
    )
    try:
        active_features = resolve_active_features(
            selected_feature_profile,
            explicit_features,
            enable_features,
            disable_features,
            apply_auto_patches=apply_auto_patches,
        )
    except ValueError as exc:
        raise SystemExit(str(exc))

    if args.write_features_config:
        output_path = write_feature_config(
            path_value=args.write_features_config,
            selected_feature_profile=selected_feature_profile,
            active_features=active_features,
            enable_features=enable_features,
            disable_features=disable_features,
            apply_auto_patches=apply_auto_patches,
        )
        print(f"Wrote feature config: {{output_path}}")

    new_details = None
    if mode == "new":
        if args.non_interactive or args.intent or args.compliance or args.custom_frameworks or args.custom_config:
            intent_input = (args.intent or "general-app").strip().lower()
            compliance_keys = parse_compliance_input((args.compliance or "").strip())
            custom_config = load_custom_config((args.custom_config or "").strip())

            config_custom_frameworks = custom_config.get("custom_frameworks")
            if isinstance(config_custom_frameworks, list):
                config_framework_items = [str(item).strip() for item in config_custom_frameworks if str(item).strip()]
            else:
                config_framework_items = parse_csv_items(str(config_custom_frameworks or ""))

            custom_frameworks = merge_unique(
                parse_csv_items((args.custom_frameworks or "").strip()),
                config_framework_items,
            )
            custom_compliance_rules = normalize_custom_compliance_rules(
                custom_config.get("custom_compliance_rules")
            )
            custom_feature_templates = normalize_custom_feature_templates(
                custom_config.get("custom_feature_templates")
            )
            
            # Parse compliance level
            compliance_level = 1  # default
            if args.compliance_level:
                try:
                    level = int(args.compliance_level)
                    if level in (0, 1, 2, 3):
                        compliance_level = level
                except ValueError:
                    pass
            
            new_details = {{
                "target_os": GENERATOR_TARGET_OS if GENERATOR_TARGET_OS != "auto" else "auto",
                "locale": (args.locale or "en").strip().lower() or "en",
                "compliance_region": (args.compliance_region or "").strip().lower(),
                "app_intent": slugify_intent_key(intent_input),
                "app_intent_input": intent_input,
                "compliance_keys": compliance_keys,
                "compliance_level": compliance_level,
                "agents": list(DEFAULT_AGENTS),
                "languages": [],
                "frameworks": [],
                "custom_frameworks": custom_frameworks,
                "custom_compliance_rules": custom_compliance_rules,
                "custom_feature_templates": custom_feature_templates,
                "tests": [],
                "linting": [],
                "suggestions": [],
            }}
        elif args.check:
            print("Check mode cannot prompt for new-project questions. Use --mode existing or add --non-interactive.")
            raise SystemExit(2)
        else:
            new_details = ask_new_project_details()
        if new_details.get("languages"):
            stack["languages"] = sorted(set(stack.get("languages", []) + new_details["languages"]))
        if new_details.get("frameworks"):
            stack["frameworks"] = sorted(set(stack.get("frameworks", []) + new_details["frameworks"]))
        if new_details.get("custom_frameworks"):
            stack["frameworks"] = sorted(
                set(stack.get("frameworks", []) + new_details["custom_frameworks"])
            )

    generated_at = resolve_generated_at(project_dir, args.check)
    ctx = build_common_context(mode, stack, new_details, generated_at)
    ctx["apply_auto_patches"] = apply_auto_patches
    ctx["patch_allowlist"] = parse_csv_items(args.patch_allowlist or "")
    ctx["patch_denylist"] = parse_csv_items(args.patch_denylist or "")
    ctx["active_features"] = active_features
    ctx["selected_feature_profile"] = selected_feature_profile
    run_start = time.perf_counter()
    dry_run = bool(args.dry_run)
    generated_files, changed_files = generate_files(
        project_dir,
        ctx,
        markdown_context,
        check_mode=args.check or dry_run,
    )

    run_metrics = build_run_metrics(
        project_dir,
        mode,
        check_mode=bool(args.check),
        dry_run=dry_run,
        generated_files=generated_files,
        changed_files=changed_files,
        start_time=run_start,
        ctx=ctx,
    )

    if args.track_performance:
        perf_path = resolve_output_path(project_dir, args.performance_history_path)
        perf_result = update_performance_history(perf_path, run_metrics)
        run_metrics["performance"] = perf_result
        if perf_result.get("regression"):
            baseline = perf_result.get("baseline_duration_ms")
            current = perf_result.get("current_duration_ms")
            print(f"WARNING: performance regression detected (current={{current}}ms, baseline={{baseline}}ms)")

    if args.json_report_path:
        report_json_path = resolve_output_path(project_dir, args.json_report_path)
        write_json_report(report_json_path, run_metrics)

    if not args.check and not dry_run:
        session_state_path = resolve_output_path(project_dir, args.session_state_path)
        write_session_state(
            session_state_path,
            {{
                "timestamp": run_metrics.get("timestamp"),
                "mode": mode,
                "project": str(project_dir),
                "selected_feature_profile": selected_feature_profile or "custom",
                "active_features": list(active_features),
                "context_window": {{
                    "max_files": context_max_files,
                    "preview_chars": context_preview_chars,
                    "files_used": len(markdown_context),
                }},
                "run_metrics": {{
                    "duration_ms": int(run_metrics.get("duration_ms", 0)),
                    "managed_files": int(run_metrics.get("managed_files", 0)),
                    "changed_files": int(run_metrics.get("changed_files", 0)),
                }},
            }},
        )

    if args.check:
        if changed_files:
            print("\\nAI docs are out of date. Regenerate with the bootstrap script.")
            for file_name in changed_files:
                print(f"- {{file_name}}")
            reasons = compute_stale_reasons(project_dir, ctx)
            if reasons:
                print("\\nLikely reasons:")
                for reason in reasons:
                    print(f"- {{reason}}")
            if args.report_path:
                write_check_report((project_dir / args.report_path).resolve(), changed_files, reasons, project_dir)
            raise SystemExit(1)
        if args.report_path:
            write_check_report((project_dir / args.report_path).resolve(), [], [], project_dir)
        print("\\nAI docs are up to date.")
        raise SystemExit(0)

    if dry_run:
        print("\\nAI docs dry-run summary")
        print(f"Project: {{project_dir}}")
        print(f"Mode: {{mode}}")
        print(f"Managed files (planned): {{len(generated_files)}}")
        print(f"Files that would change: {{len(changed_files)}}")
        print(f"Active features: {{', '.join(active_features) if active_features else '(none)'}}")
        for file_name in changed_files:
            print(f"- {{file_name}}")
        raise SystemExit(0)

    print("\\nAI docs generation complete.")
    print(f"Project: {{project_dir}}")
    print(f"Mode: {{mode}}")
    print(f"Managed files: {{len(generated_files)}}")
    print(f"Files changed: {{len(changed_files)}}")
    print(f"Active features: {{', '.join(active_features) if active_features else '(none)'}}")
    for file_name in changed_files:
        print(f"- {{file_name}}")

    if new_details and new_details.get("suggestions"):
        print("\\nSuggested next steps:")
        for item in new_details["suggestions"]:
            print(f"- {{item}}")


if __name__ == "__main__":
    main()'''
