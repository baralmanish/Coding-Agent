"""Framework and package guidance hints."""

FRAMEWORK_INTENT_HINTS = {
    "Next.js": {"E-Commerce": 2, "AdTech": 1},
    "React": {"Social App": 1, "E-Commerce": 1},
    "Express": {"Ride Booking": 1, "E-Commerce": 1, "AdTech": 1},
    "Fastify": {"Ride Booking": 1, "AdTech": 1},
    "NestJS": {"B2B SaaS": 1, "IoT Platform": 1},
    "Laravel": {"E-Commerce": 2, "CRM": 1},
    "FastAPI": {"Analytics": 1, "Health Tech": 1, "Scraper / Data Ingestion": 1},
    "Django": {"CRM": 1, "EdTech": 1, "Health Tech": 1},
    "Spring Boot": {"B2B SaaS": 1, "GovTech": 1},
    "ASP.NET Core": {"B2B SaaS": 1, "GovTech": 1},
}

PACKAGE_GUIDANCE = {
    "React": {
        "recommended": [
            "react-query (@tanstack/react-query)",
            "zod",
            "react-hook-form",
            "date-fns",
        ],
        "avoid": [
            "moment -> prefer date-fns/dayjs",
            "redux-form -> prefer react-hook-form",
        ],
    },
    "Next.js": {
        "recommended": [
            "next-safe-action",
            "zod",
            "@tanstack/react-query",
            "next-auth/auth.js",
        ],
        "avoid": ["next-routes -> use App Router", "moment -> prefer date-fns/dayjs"],
    },
    "Express": {
        "recommended": ["zod", "pino", "helmet", "rate-limiter-flexible"],
        "avoid": [
            "request -> use native fetch/undici",
            "winston-only stacks -> consider pino for perf",
        ],
    },
    "Fastify": {
        "recommended": ["@fastify/helmet", "@fastify/rate-limit", "zod", "pino"],
        "avoid": ["request -> use native fetch/undici"],
    },
    "NestJS": {
        "recommended": [
            "class-validator",
            "class-transformer",
            "@nestjs/swagger",
            "pino",
        ],
        "avoid": ["request -> use native fetch/undici"],
    },
    "Vue": {
        "recommended": ["pinia", "vue-query", "zod", "dayjs"],
        "avoid": ["moment -> prefer dayjs/date-fns"],
    },
    "Angular": {
        "recommended": ["ngrx", "zod", "rxjs", "date-fns"],
        "avoid": ["tslint -> use eslint"],
    },
    "Laravel": {
        "recommended": [
            "laravel/sanctum",
            "spatie/laravel-permission",
            "laravel/pint",
            "larastan/larastan",
        ],
        "avoid": [
            "abandoned packages in composer.lock -> replace with maintained alternatives"
        ],
    },
    "FastAPI": {
        "recommended": ["pydantic-settings", "httpx", "sqlmodel/alembic", "structlog"],
        "avoid": [
            "requests in async routes -> use httpx",
            "pydantic v1-only libs -> prefer v2-ready libs",
        ],
    },
    "Django": {
        "recommended": [
            "django-environ",
            "django-filter",
            "djangorestframework",
            "sentry-sdk",
        ],
        "avoid": ["django-rest-swagger -> use drf-spectacular"],
    },
}

SECURITY_AUDIT_COMMANDS = {
    "npm/pnpm/yarn": [
        "npm audit --omit=dev",
        "pnpm audit",
        "yarn npm audit",
    ],
    "pip/poetry": [
        "python -m pip install pip-audit",
        "pip-audit",
        "poetry export -f requirements.txt --without-hashes | pip-audit -r /dev/stdin",
    ],
    "composer": [
        "composer audit",
    ],
    "go modules": [
        "go install golang.org/x/vuln/cmd/govulncheck@latest",
        "govulncheck ./...",
    ],
    "cargo": [
        "cargo install cargo-audit",
        "cargo audit",
    ],
    "nuget": [
        "dotnet list package --vulnerable --include-transitive",
    ],
    "maven/gradle": [
        "mvn org.owasp:dependency-check-maven:check",
        "./gradlew dependencyCheckAnalyze",
    ],
    "bundler": [
        "bundle audit check --update",
    ],
    "SwiftPM": [
        "swift package resolve && swift package show-dependencies",
    ],
}
