"""
Utility functions extracted from setup-ai-docs.py for better organization and reusability.

This module contains all non-bootstrap utility functions organized by category:
- Time/hash utilities
- File I/O and project detection
- Text processing and compliance parsing
- Stack detection and framework analysis
- Package guidance
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except Exception:
    tomllib = None

from .constants import (
    COMPLIANCE_ALIASES,
    COMPLIANCE_PACKS,
    FRAMEWORK_INTENT_HINTS,
    PACKAGE_GUIDANCE,
    SECURITY_AUDIT_COMMANDS,
)


# ============================================================================
# TIME & HASH UTILITIES
# ============================================================================


def now_utc() -> str:
    """Get current UTC timestamp as formatted string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def hash_text(content: str) -> str:
    """Calculate SHA256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def current_script_sha256() -> str:
    """Get SHA256 hash of the current script file."""
    try:
        content = Path(__file__).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return hash_text(content)


# ============================================================================
# PROJECT DETECTION
# ============================================================================


def detect_project_type(project_dir: Path) -> str:
    """Detect if project is 'existing' or 'new' based on manifest/source files."""
    manifest_candidates = [
        "package.json",
        "composer.json",
        "Package.swift",
        "pyproject.toml",
        "requirements.txt",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
        "Gemfile",
    ]
    has_manifest = any((project_dir / name).exists() for name in manifest_candidates)
    has_source = any(
        (project_dir / d).exists()
        for d in ["src", "app", "services", "backend", "frontend"]
    )
    has_docs = any(project_dir.glob("*.md"))
    has_xcodeproj = any(project_dir.glob("*.xcodeproj")) or any(
        project_dir.glob("*.xcworkspace")
    )
    return (
        "existing"
        if (has_manifest or has_source or has_docs or has_xcodeproj)
        else "new"
    )


def read_json_file(path: Path) -> dict[str, Any]:
    """Safely read JSON file, returning empty dict if missing or invalid."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def parse_requirements_txt(path: Path) -> list[str]:
    """Parse pip requirements.txt and extract dependency names."""
    deps = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        dep = re.split(r"[<>=~! ]", line, maxsplit=1)[0].strip()
        if dep:
            deps.append(dep)
    return deps


def parse_toml_dependencies(path: Path) -> list[str]:
    """Parse pyproject.toml and poetry dependencies."""
    if not tomllib:
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    deps = []
    project = data.get("project", {})
    for dep in project.get("dependencies", []) or []:
        dep_name = re.split(r"[<>=~! ]", dep, maxsplit=1)[0].strip()
        if dep_name:
            deps.append(dep_name)

    poetry = data.get("tool", {}).get("poetry", {})
    poetry_deps = poetry.get("dependencies", {})
    for name in poetry_deps:
        if name.lower() != "python":
            deps.append(name)

    return sorted(set(deps))


def gather_existing_markdown_context(
    project_dir: Path, max_files: int = 20
) -> list[dict[str, Any]]:
    """Gather existing markdown files for context (excluding generated files)."""
    generated_roots = (
        "AGENTS.md",
        "AI_DOCS_INDEX.md",
        "CLAUDE.md",
        "CODEX.md",
        "ANTIGRAVITY.md",
    )
    docs = []
    for md_file in sorted(project_dir.rglob("*.md")):
        rel = md_file.relative_to(project_dir).as_posix()
        if (
            rel.startswith(".git/")
            or rel.startswith(".ai-docs/")
            or rel.startswith(".github/")
            or rel.startswith(".cursor/")
        ):
            continue
        if rel in generated_roots:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        docs.append({"path": rel, "preview": content[:500].strip()})
        if len(docs) >= max_files:
            break
    return docs


# ============================================================================
# TEXT PROCESSING & COMPLIANCE PARSING
# ============================================================================


def merge_unique(existing: list[str], incoming: list[str]) -> list[str]:
    """Merge two lists removing duplicates while preserving order."""
    merged = []
    seen = set()
    for item in (existing or []) + (incoming or []):
        value = item.strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(value)
    return merged


def slugify_intent_key(value: str) -> str:
    """Convert input text to slugified intent key (e.g., 'E-Commerce' -> 'e-commerce')."""
    key = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return key or "general-app"


def keyword_confidence_score(raw: str, keyword: str) -> tuple[int, bool]:
    """Calculate confidence score for keyword match (whole word > substring)."""
    text = raw.lower()
    k = keyword.lower()
    if not k:
        return 0, False

    whole_word = re.search(rf"\b{re.escape(k)}\b", text) is not None
    if whole_word:
        return 3, True
    if k in text:
        return 1, True
    return 0, False


def parse_compliance_input(raw: str) -> list[str]:
    """Parse comma-separated compliance pack input with alias resolution."""
    if not raw.strip():
        return []

    items = []
    for part in raw.split(","):
        key = slugify_intent_key(part)
        mapped = COMPLIANCE_ALIASES.get(key)
        if mapped:
            items.append(mapped)
    return merge_unique([], items)


def resolve_compliance_packs(
    app_intent_input: str, selected_keys: list[str] | None = None
) -> list[dict[str, Any]]:
    """Resolve compliance packs based on app intent keywords and explicit selection."""
    selected = merge_unique([], selected_keys or [])
    low = (app_intent_input or "").lower()

    for pack_key, pack in COMPLIANCE_PACKS.items():
        trigger_words = pack.get("trigger_keywords", [])
        if any(word in low for word in trigger_words):
            selected = merge_unique(selected, [pack_key])

    resolved = []
    for key in selected:
        pack = COMPLIANCE_PACKS.get(key)
        if not pack:
            continue
        resolved.append(
            {
                "key": key,
                "name": pack.get("name", key.upper()),
                "checks": pack.get("checks", []),
            }
        )

    return resolved


def compute_framework_intent_bonus(stack: dict[str, Any] | None) -> dict[str, int]:
    """Compute intent bonuses based on detected frameworks."""
    bonuses = {}
    if not stack:
        return bonuses

    for framework in stack.get("frameworks", []) or []:
        hint = FRAMEWORK_INTENT_HINTS.get(framework, {})
        for label, value in hint.items():
            bonuses[label] = bonuses.get(label, 0) + int(value)
    return bonuses


def resolve_package_guidance(stack: dict[str, Any]) -> dict[str, Any]:
    """Resolve package recommendations based on detected stack."""
    frameworks = stack.get("frameworks", []) or []
    package_managers = stack.get("package_managers", []) or []

    recommended = []
    avoid = []
    matched_profiles = []

    for framework in frameworks:
        profile = PACKAGE_GUIDANCE.get(framework)
        if not profile:
            continue
        matched_profiles.append(framework)
        recommended = merge_unique(recommended, profile.get("recommended", []))
        avoid = merge_unique(avoid, profile.get("avoid", []))

    languages = {item.lower() for item in (stack.get("languages", []) or [])}
    if not matched_profiles:
        if "python" in languages:
            recommended = merge_unique(
                recommended, ["ruff", "mypy", "pytest", "pip-audit"]
            )
            avoid = merge_unique(
                avoid, ["unmaintained python deps without recent releases"]
            )
        if "typescript" in languages or "javascript" in languages:
            recommended = merge_unique(
                recommended, ["zod", "eslint", "prettier", "vitest"]
            )
            avoid = merge_unique(
                avoid,
                [
                    "request -> use native fetch/undici",
                    "moment -> prefer date-fns/dayjs",
                ],
            )
        if "php" in languages:
            recommended = merge_unique(
                recommended, ["phpstan/larastan", "php-cs-fixer"]
            )
            avoid = merge_unique(avoid, ["abandoned composer packages"])

    audit_commands = []
    for pm in package_managers:
        audit_commands = merge_unique(
            audit_commands, SECURITY_AUDIT_COMMANDS.get(pm, [])
        )

    if not audit_commands:
        audit_commands = [
            "Run ecosystem-specific vulnerability scanning before introducing new dependencies."
        ]

    return {
        "matched_profiles": matched_profiles,
        "recommended_packages": recommended,
        "avoid_packages": avoid,
        "audit_commands": audit_commands,
    }


# ============================================================================
# STACK DETECTION
# ============================================================================


def detect_stack(project_dir: Path) -> dict[str, Any]:
    """Detect project tech stack by analyzing manifest files and source directories."""
    languages = set()
    frameworks = set()
    package_managers = set()
    packages = set()
    scripts = {}

    # Node.js/JavaScript/TypeScript
    package_json = project_dir / "package.json"
    if package_json.exists():
        languages.update(["JavaScript", "TypeScript"])
        package_managers.add("npm/pnpm/yarn")
        data = read_json_file(package_json)
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}
        packages.update(all_deps.keys())
        scripts = data.get("scripts", {})

        framework_map = {
            "react": "React",
            "react-native": "React Native",
            "next": "Next.js",
            "vue": "Vue",
            "nuxt": "Nuxt",
            "svelte": "Svelte",
            "@angular/core": "Angular",
            "express": "Express",
            "@nestjs/core": "NestJS",
            "nestjs": "NestJS",
            "fastify": "Fastify",
            "hono": "Hono",
            "astro": "Astro",
            "@remix-run/react": "Remix",
        }
        for dep_name, fw in framework_map.items():
            if dep_name in all_deps:
                frameworks.add(fw)

    # PHP/Composer
    composer_json = project_dir / "composer.json"
    if composer_json.exists():
        languages.add("PHP")
        package_managers.add("composer")
        data = read_json_file(composer_json)
        req = data.get("require", {})
        req_dev = data.get("require-dev", {})
        all_php = {**req, **req_dev}
        packages.update(all_php.keys())

        php_framework_map = {
            "laravel/framework": "Laravel",
            "laravel/lumen-framework": "Lumen",
            "symfony/symfony": "Symfony",
        }
        for dep_name, fw in php_framework_map.items():
            if dep_name in all_php:
                frameworks.add(fw)

    # Python
    pyproject = project_dir / "pyproject.toml"
    requirements = project_dir / "requirements.txt"
    if pyproject.exists() or requirements.exists():
        languages.add("Python")
        package_managers.add("pip/poetry")
        if pyproject.exists():
            packages.update(parse_toml_dependencies(pyproject))
        if requirements.exists():
            packages.update(parse_requirements_txt(requirements))

        py_framework_map = {
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "pydantic": "Pydantic",
        }
        pkg_lower = {p.lower() for p in packages}
        for dep_name, fw in py_framework_map.items():
            if dep_name in pkg_lower:
                frameworks.add(fw)

    # Other languages
    if (project_dir / "go.mod").exists():
        languages.add("Go")
        package_managers.add("go modules")

    if (project_dir / "Cargo.toml").exists():
        languages.add("Rust")
        package_managers.add("cargo")

    if list(project_dir.glob("*.csproj")):
        languages.add("C#")
        package_managers.add("nuget")

    if (project_dir / "pom.xml").exists() or (project_dir / "build.gradle").exists():
        languages.add("Java")
        package_managers.add("maven/gradle")

    if (project_dir / "Gemfile").exists():
        languages.add("Ruby")
        package_managers.add("bundler")

    # Swift/iOS
    package_swift = project_dir / "Package.swift"
    if package_swift.exists():
        languages.add("Swift")
        package_managers.add("SwiftPM")
        try:
            swift_text = package_swift.read_text(
                encoding="utf-8", errors="ignore"
            ).lower()
        except Exception:
            swift_text = ""

        if "vapor" in swift_text:
            frameworks.add("Vapor")
        if "swiftui" in swift_text:
            frameworks.add("SwiftUI")

    has_xcodeproj = any(project_dir.glob("*.xcodeproj")) or any(
        project_dir.glob("*.xcworkspace")
    )
    if has_xcodeproj:
        languages.add("Swift")
        package_managers.add("Xcode")
        if not frameworks:
            frameworks.add("SwiftUI")

    return {
        "languages": sorted(languages),
        "frameworks": sorted(frameworks),
        "package_managers": sorted(package_managers),
        "packages": sorted(packages),
        "scripts": scripts,
    }
