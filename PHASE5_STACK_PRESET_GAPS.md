# Phase 5 Stack Preset Gap Analysis

## Baseline

Before this update, preset coverage was concentrated around:

- TypeScript frontend and Node API stacks
- Python FastAPI and Django
- PHP Laravel
- Java Spring Boot
- .NET Web API
- Swift (Vapor and iOS)

## Identified Gaps

1. Modern React meta-framework alternative to Next.js was missing.
2. Python lightweight API preset outside FastAPI/Django was missing.
3. Ruby Rails API preset was missing.
4. Java cloud-native alternative to Spring Boot was missing.
5. Elixir/Phoenix ecosystem preset was missing.
6. Content-focused modern web framework preset was missing.

## Added Presets

1. remix
2. flask-api
3. rails-api
4. quarkus
5. phoenix
6. astro

## Resulting Catalog Size

- Total stack presets after expansion: 25

## Source of Truth Changes

- Added shared STACK_PRESETS to src/constants/presets.py.
- Exported STACK_PRESETS in src/constants/**init**.py.
- Updated setup-ai-docs.py builder to embed presets from constants instead of duplicate inline dictionary.

## Validation

- ai-docs-bootstrap --list-stack-presets shows all new entries.
- Full test suite passes after regeneration.
