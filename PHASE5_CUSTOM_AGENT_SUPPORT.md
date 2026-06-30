# Phase 5 Custom Agent Support

## Delivered Capabilities

1. Custom frameworks configuration
2. Custom compliance rules configuration
3. Custom feature templates configuration

## Configuration Inputs

Supported in new-project mode through:

- --custom-frameworks with comma-separated values
- --custom-config JSON file path

Custom config JSON supports keys:

- custom_frameworks: list or CSV string
- custom_compliance_rules: list of objects with key, name, checks
- custom_feature_templates: list of objects with name and template

## Generation Behavior

- Custom frameworks are merged into detected frameworks for context and guidance.
- Custom compliance rules are appended to resolved compliance packs.
- Custom feature templates are materialized to .specs/features/<name>/spec.md.
- A summary file is generated at .ai-docs/CUSTOM-AGENT-CONFIG.md.

## Validation

- Added integration coverage in tests/test_bootstrap_integration.py.
- Full test suite passes.
- End-to-end CLI execution verified with a sample custom config JSON.
