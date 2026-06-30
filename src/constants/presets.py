"""App archetypes and domain-specific blueprints."""

STACK_PRESETS = {
    "react-ts": {
        "languages": ["TypeScript"],
        "frameworks": ["React"],
        "tests": ["vitest", "@testing-library/react"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Enable strict tsconfig and type-aware ESLint rules.",
            "Use Testing Library with Vitest for component and integration tests.",
        ],
    },
    "next-ts": {
        "languages": ["TypeScript"],
        "frameworks": ["Next.js"],
        "tests": ["vitest", "playwright"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Adopt route-level testing and API contract checks.",
            "Use preview deployments to validate doc-guided workflows.",
        ],
    },
    "node-api": {
        "languages": ["TypeScript"],
        "frameworks": ["Express"],
        "tests": ["vitest", "supertest"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Validate request/response schemas at boundaries.",
            "Add integration tests for critical API paths.",
        ],
    },
    "express-ts": {
        "languages": ["TypeScript"],
        "frameworks": ["Express"],
        "tests": ["vitest", "supertest"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Define API contracts and validate request/response payloads.",
            "Use centralized error handling and structured logging.",
        ],
    },
    "fastify-ts": {
        "languages": ["TypeScript"],
        "frameworks": ["Fastify"],
        "tests": ["vitest", "supertest"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Use schema-first routes for validation and speed.",
            "Enable serialization and benchmark critical endpoints.",
        ],
    },
    "nestjs": {
        "languages": ["TypeScript"],
        "frameworks": ["NestJS"],
        "tests": ["jest", "supertest"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Organize by bounded modules and enforce DTO validation.",
            "Use e2e test modules for critical workflows.",
        ],
    },
    "angular": {
        "languages": ["TypeScript"],
        "frameworks": ["Angular"],
        "tests": ["jest", "cypress"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Use strict template/type checks and standalone components.",
            "Add component integration tests for key user journeys.",
        ],
    },
    "vue": {
        "languages": ["TypeScript"],
        "frameworks": ["Vue"],
        "tests": ["vitest", "@vue/test-utils", "playwright"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Adopt composables for reusable logic and better testability.",
            "Add route-level tests for stateful flows.",
        ],
    },
    "react-native": {
        "languages": ["TypeScript"],
        "frameworks": ["React Native"],
        "tests": ["jest", "@testing-library/react-native", "detox"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Separate UI and platform services to simplify testing.",
            "Validate navigation and offline scenarios with e2e tests.",
        ],
    },
    "laravel": {
        "languages": ["PHP"],
        "frameworks": ["Laravel"],
        "tests": ["phpunit", "pest"],
        "linting": ["php-cs-fixer", "larastan"],
        "suggestions": [
            "Use form requests/policies for validation and authorization.",
            "Cover jobs/events and critical endpoints with feature tests.",
        ],
    },
    "nuxt": {
        "languages": ["TypeScript"],
        "frameworks": ["Nuxt"],
        "tests": ["vitest", "playwright"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Use server routes and composables with explicit contracts.",
            "Add rendering and navigation tests for core pages.",
        ],
    },
    "sveltekit": {
        "languages": ["TypeScript"],
        "frameworks": ["SvelteKit"],
        "tests": ["vitest", "playwright"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Keep load/actions predictable and strongly typed.",
            "Test server/client boundaries for auth and data flows.",
        ],
    },
    "django": {
        "languages": ["Python"],
        "frameworks": ["Django"],
        "tests": ["pytest", "pytest-django"],
        "linting": ["ruff", "mypy"],
        "suggestions": [
            "Use service-layer patterns for complex business logic.",
            "Add integration tests for ORM queries and permissions.",
        ],
    },
    "go-fiber": {
        "languages": ["Go"],
        "frameworks": ["Fiber"],
        "tests": ["go test"],
        "linting": ["golangci-lint"],
        "suggestions": [
            "Keep handlers thin and move business logic to services.",
            "Use benchmarks for high-throughput endpoints.",
        ],
    },
    "spring-boot": {
        "languages": ["Java"],
        "frameworks": ["Spring Boot"],
        "tests": ["junit", "testcontainers"],
        "linting": ["checkstyle", "spotbugs"],
        "suggestions": [
            "Use layered architecture with clear domain boundaries.",
            "Add integration tests for repositories and APIs.",
        ],
    },
    "dotnet-webapi": {
        "languages": ["C#"],
        "frameworks": ["ASP.NET Core"],
        "tests": ["xunit"],
        "linting": ["dotnet format"],
        "suggestions": [
            "Use DTO validation and strict API contracts.",
            "Add integration tests with WebApplicationFactory.",
        ],
    },
    "swift-vapor": {
        "languages": ["Swift"],
        "frameworks": ["Vapor"],
        "tests": ["xctest"],
        "linting": ["swift-format", "swiftlint"],
        "suggestions": [
            "Use typed DTOs and explicit validation for request handlers.",
            "Add integration tests for routes and middleware pipelines.",
        ],
    },
    "swift-ios": {
        "languages": ["Swift"],
        "frameworks": ["SwiftUI"],
        "tests": ["xctest"],
        "linting": ["swift-format", "swiftlint"],
        "suggestions": [
            "Structure state with clear view-model boundaries for testability.",
            "Add UI and unit tests for navigation, state transitions, and error paths.",
        ],
    },
    "fastapi": {
        "languages": ["Python"],
        "frameworks": ["FastAPI"],
        "tests": ["pytest"],
        "linting": ["ruff", "mypy"],
        "suggestions": [
            "Use pydantic models for strict input/output validation.",
            "Add contract tests for OpenAPI schema compatibility.",
        ],
    },
    "remix": {
        "languages": ["TypeScript"],
        "frameworks": ["Remix"],
        "tests": ["vitest", "playwright"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Test loaders/actions with strict request boundary contracts.",
            "Validate nested route data dependencies with integration tests.",
        ],
    },
    "flask-api": {
        "languages": ["Python"],
        "frameworks": ["Flask"],
        "tests": ["pytest"],
        "linting": ["ruff", "mypy"],
        "suggestions": [
            "Use blueprint separation and schema validation at API edges.",
            "Add contract tests for auth, pagination, and error handling.",
        ],
    },
    "phoenix": {
        "languages": ["Elixir"],
        "frameworks": ["Phoenix"],
        "tests": ["mix test"],
        "linting": ["mix format", "credo"],
        "suggestions": [
            "Model contexts around bounded domains and explicit contracts.",
            "Use integration tests for channels, auth, and background workflows.",
        ],
    },
    "rails-api": {
        "languages": ["Ruby"],
        "frameworks": ["Rails"],
        "tests": ["rspec"],
        "linting": ["rubocop", "brakeman"],
        "suggestions": [
            "Keep services and policies explicit for complex business rules.",
            "Add request specs for auth, tenancy, and error behavior.",
        ],
    },
    "quarkus": {
        "languages": ["Java"],
        "frameworks": ["Quarkus"],
        "tests": ["junit"],
        "linting": ["checkstyle", "spotbugs"],
        "suggestions": [
            "Use profile-driven config and CDI boundaries for modular services.",
            "Add testcontainers-backed tests for persistence and messaging.",
        ],
    },
    "astro": {
        "languages": ["TypeScript"],
        "frameworks": ["Astro"],
        "tests": ["vitest", "playwright"],
        "linting": ["eslint", "prettier"],
        "suggestions": [
            "Use island boundaries deliberately to keep hydration predictable.",
            "Test content collections and route generation for SEO-critical pages.",
        ],
    },
}

APP_ARCHETYPES = {
    "general-app": {
        "label": "General App",
        "description": "Balanced defaults for product and platform features.",
        "capabilities": [
            "Authentication and authorization",
            "Core CRUD/API workflows",
            "Observability (logs, metrics, traces)",
        ],
        "suggestions": [
            "Define clear domain modules and API boundaries early.",
            "Add integration tests for high-value user workflows.",
        ],
    },
    "chatbot": {
        "label": "Chatbot",
        "description": "Conversational product with retrieval and safety controls.",
        "capabilities": [
            "Conversation/session state",
            "Prompt and tool orchestration",
            "Knowledge retrieval (RAG) and grounding",
            "Guardrails, moderation, and abuse controls",
        ],
        "suggestions": [
            "Version prompts and evaluate responses against test datasets.",
            "Implement latency/error budgets for model and retrieval calls.",
            "Add red-team safety cases and policy checks in CI.",
        ],
    },
    "crm": {
        "label": "CRM",
        "description": "Business application with multi-role workflows and data integrity.",
        "capabilities": [
            "Accounts/contacts/opportunities lifecycle",
            "Role-based access control and audit logs",
            "Search/filter/reporting dashboards",
            "Background jobs and integration webhooks",
        ],
        "suggestions": [
            "Model entities and relationships before implementing endpoints/UI.",
            "Enforce RBAC and auditability for all sensitive mutations.",
            "Add migration and seed strategy for predictable environments.",
        ],
    },
}

INTENT_KEYWORD_BLUEPRINTS = [
    (
        ["analytics", "bi", "dashboard", "reporting"],
        {
            "label": "Analytics",
            "capabilities": [
                "Event ingestion and schema validation",
                "Aggregation pipelines and materialized views",
                "Role-based dashboards and export workflows",
            ],
            "suggestions": [
                "Define event taxonomy/versioning before implementation.",
                "Add data quality and backfill verification checks in CI.",
            ],
        },
    ),
    (
        ["crash", "logger", "error", "observability", "monitoring"],
        {
            "label": "Crash Logger",
            "capabilities": [
                "Client/server error capture pipelines",
                "Deduplication, fingerprinting, and issue grouping",
                "Alert routing and incident triage workflows",
            ],
            "suggestions": [
                "Capture structured context while redacting sensitive data.",
                "Define alert severity SLOs to reduce notification noise.",
            ],
        },
    ),
    (
        ["social", "community", "feed", "network"],
        {
            "label": "Social App",
            "capabilities": [
                "Profiles, follows/friendships, and privacy controls",
                "Feed ranking, reactions, and comment moderation",
                "Notifications and abuse-report workflows",
            ],
            "suggestions": [
                "Design moderation and anti-abuse controls from day one.",
                "Use idempotent event processing for feed and notification fanout.",
            ],
        },
    ),
    (
        ["wallet", "ewallet", "e-wallet", "payments", "fintech"],
        {
            "label": "E-Wallet",
            "capabilities": [
                "Ledger-based balances and transaction history",
                "KYC/compliance gates and fraud checks",
                "Reconciliation jobs and dispute workflows",
            ],
            "suggestions": [
                "Use append-only transaction logs and idempotency keys.",
                "Enforce strict authorization and audit trails on money movement.",
            ],
        },
    ),
    (
        ["chat", "messaging", "whatsapp", "telegram"],
        {
            "label": "Chat App",
            "capabilities": [
                "Real-time messaging and delivery status",
                "Presence, typing indicators, and unread state",
                "Media attachments and retention policies",
            ],
            "suggestions": [
                "Use durable message ids and retry-safe delivery semantics.",
                "Add abuse/spam protection and privacy-preserving defaults.",
            ],
        },
    ),
    (
        ["ride", "booking", "mobility", "taxi", "cab"],
        {
            "label": "Ride Booking",
            "capabilities": [
                "Rider/driver matching and dispatch",
                "Live location tracking and ETA updates",
                "Fare calculation, wallet, and trip settlement",
            ],
            "suggestions": [
                "Use geospatial indexing and event-driven trip state transitions.",
                "Design retry-safe booking/payment workflows with idempotency keys.",
            ],
        },
    ),
    (
        ["ecommerce", "e-commerce", "commerce", "marketplace", "shop", "store"],
        {
            "label": "E-Commerce",
            "capabilities": [
                "Catalog/search, cart, and checkout flows",
                "Inventory, order lifecycle, and fulfillment",
                "Promotions, returns, and payment integration",
            ],
            "suggestions": [
                "Model order states explicitly and keep payment webhooks idempotent.",
                "Add anti-fraud, stock reservation, and reconciliation workflows.",
            ],
        },
    ),
    (
        ["scraper", "scrapping", "scraping", "crawler", "crawl", "extract"],
        {
            "label": "Scraper / Data Ingestion",
            "capabilities": [
                "Crawl scheduling and polite rate limiting",
                "Parsing, normalization, and deduplication pipelines",
                "Storage, retry queues, and failure recovery",
            ],
            "suggestions": [
                "Respect robots.txt/terms and enforce adaptive throttling.",
                "Use deterministic parsing contracts and monitor extraction drift.",
            ],
        },
    ),
    (
        ["delivery", "logistics", "supply", "fulfillment"],
        {
            "label": "Delivery / Logistics",
            "capabilities": [
                "Shipment planning and routing workflows",
                "Real-time package status and exception handling",
                "Proof-of-delivery and partner integrations",
            ],
            "suggestions": [
                "Track route and status transitions as immutable events.",
                "Build SLA alerts for delayed or failed fulfillment stages.",
            ],
        },
    ),
    (
        ["saas", "b2b", "multi-tenant", "tenant"],
        {
            "label": "B2B SaaS",
            "capabilities": [
                "Multi-tenant data isolation and tenant configuration",
                "Subscription/billing and feature entitlements",
                "Admin controls, audit logs, and SSO",
            ],
            "suggestions": [
                "Enforce tenant scoping in every query and API boundary.",
                "Model feature flags/plan entitlements as first-class policies.",
            ],
        },
    ),
    (
        ["video", "streaming", "ott", "media"],
        {
            "label": "Media / Streaming",
            "capabilities": [
                "Content ingestion/transcoding pipeline",
                "Playback sessions, recommendations, and watch state",
                "DRM/access control and CDN delivery strategy",
            ],
            "suggestions": [
                "Use async job orchestration for media processing stages.",
                "Track QoE metrics (startup time, buffering, failure rate).",
            ],
        },
    ),
    (
        ["realtime", "real-time", "collaboration", "whiteboard", "doc"],
        {
            "label": "Realtime Collaboration",
            "capabilities": [
                "Concurrent editing/session presence",
                "Conflict resolution and state synchronization",
                "Permissions and activity history",
            ],
            "suggestions": [
                "Use CRDT/OT-inspired models for concurrent edits.",
                "Persist operation logs for replay and debugging.",
            ],
        },
    ),
    (
        ["health", "clinic", "ehr", "emr", "telemedicine"],
        {
            "label": "Health Tech",
            "capabilities": [
                "Patient/provider workflows and scheduling",
                "Clinical records and consent management",
                "Secure messaging and compliance audit trails",
            ],
            "suggestions": [
                "Apply strict data minimization, encryption, and retention controls.",
                "Enforce explicit access auditing for sensitive record access.",
            ],
        },
    ),
    (
        ["edtech", "learning", "lms", "course", "quiz"],
        {
            "label": "EdTech",
            "capabilities": [
                "Course/content organization and learner progress tracking",
                "Assessments, submissions, and grading workflows",
                "Instructor dashboards and feedback loops",
            ],
            "suggestions": [
                "Model learner progress as resumable state machines.",
                "Add anti-cheating and assessment integrity checks where needed.",
            ],
        },
    ),
    (
        ["job", "recruit", "ats", "hiring", "hr"],
        {
            "label": "Recruitment / HR",
            "capabilities": [
                "Job posting and candidate pipeline management",
                "Interview scheduling and feedback workflows",
                "Role-based access and confidential note handling",
            ],
            "suggestions": [
                "Use pipeline stage transitions with explicit audit events.",
                "Enforce strict visibility rules for candidate data.",
            ],
        },
    ),
    (
        ["iot", "device", "sensor", "telemetry", "edge"],
        {
            "label": "IoT Platform",
            "capabilities": [
                "Device provisioning and identity lifecycle",
                "Telemetry ingestion, alerting, and dashboards",
                "Firmware rollout and remote command workflows",
            ],
            "suggestions": [
                "Treat device identity/cert rotation as core security workflows.",
                "Use partitioned ingestion and backpressure control for burst traffic.",
            ],
        },
    ),
    (
        ["finops", "billing", "invoice", "subscription", "metering"],
        {
            "label": "Billing / FinOps",
            "capabilities": [
                "Usage metering and pricing policy engine",
                "Invoice generation and payment reconciliation",
                "Credit adjustments and dispute handling",
            ],
            "suggestions": [
                "Separate rating, billing, and invoicing into distinct services.",
                "Version pricing rules to keep historical invoices reproducible.",
            ],
        },
    ),
    (
        ["gaming", "game", "esports", "leaderboard"],
        {
            "label": "Gaming",
            "capabilities": [
                "Player progression and achievements",
                "Matchmaking and session lifecycle",
                "Leaderboards, anti-cheat, and moderation",
            ],
            "suggestions": [
                "Design anti-abuse and anti-cheat signals early.",
                "Use event sourcing for progression and reward reconciliation.",
            ],
        },
    ),
    (
        ["travel", "booking-engine", "hotel", "flight", "trip"],
        {
            "label": "Travel",
            "capabilities": [
                "Availability/pricing search and booking flows",
                "Reservation lifecycle and cancellation policies",
                "Supplier integrations and itinerary management",
            ],
            "suggestions": [
                "Treat booking state transitions as idempotent workflows.",
                "Implement supplier retry/compensation for partial failures.",
            ],
        },
    ),
    (
        ["legal", "contract", "case", "compliance-ops"],
        {
            "label": "Legal Tech",
            "capabilities": [
                "Document lifecycle and clause extraction",
                "Case/matter workflows and deadline tracking",
                "Access controls and evidentiary audit logs",
            ],
            "suggestions": [
                "Track document lineage and immutable review history.",
                "Enforce fine-grained permissions for privileged content.",
            ],
        },
    ),
    (
        ["gov", "government", "public-sector", "citizen"],
        {
            "label": "GovTech",
            "capabilities": [
                "Citizen service workflows and case handling",
                "Identity verification and role-bound approvals",
                "Records retention and transparency reporting",
            ],
            "suggestions": [
                "Model approval chains explicitly with audit evidence.",
                "Apply strict data retention and redaction controls.",
            ],
        },
    ),
    (
        ["insurance", "insurtech", "claims", "underwriting", "policy"],
        {
            "label": "InsurTech",
            "capabilities": [
                "Policy lifecycle, endorsements, and renewals",
                "Claims intake, adjudication, and payout workflows",
                "Fraud scoring and risk-based underwriting pipelines",
            ],
            "suggestions": [
                "Model policy and claim states as explicit workflow transitions.",
                "Use audit trails for every underwriting and claims decision.",
            ],
        },
    ),
    (
        ["real-estate", "proptech", "listing", "broker", "tenant"],
        {
            "label": "PropTech",
            "capabilities": [
                "Property listings, search filters, and recommendation flows",
                "Lease lifecycle, tenant onboarding, and document workflows",
                "Broker/owner permissions and transaction timelines",
            ],
            "suggestions": [
                "Separate listing discovery from transaction and contract workflows.",
                "Use immutable event logs for offer, lease, and payment milestones.",
            ],
        },
    ),
    (
        ["manufacturing", "factory", "mes", "production", "inventory-control"],
        {
            "label": "Manufacturing / MES",
            "capabilities": [
                "Production order planning and work-center scheduling",
                "Inventory traceability and quality-control checkpoints",
                "Machine telemetry ingestion and downtime analytics",
            ],
            "suggestions": [
                "Track production state changes with lot and batch lineage.",
                "Add quality-gate validation before advancing workflow stages.",
            ],
        },
    ),
    (
        ["nonprofit", "ngo", "donation", "fundraising", "grant"],
        {
            "label": "Nonprofit / Fundraising",
            "capabilities": [
                "Donor lifecycle, campaign management, and recurring giving",
                "Grant application tracking and disbursement workflows",
                "Outcome reporting and compliance evidence generation",
            ],
            "suggestions": [
                "Keep donation and grant accounting trails immutable and auditable.",
                "Model campaign attribution and donor communication preferences clearly.",
            ],
        },
    ),
    (
        ["security", "soc", "siem", "threat", "vulnerability"],
        {
            "label": "Cybersecurity Platform",
            "capabilities": [
                "Security event ingestion, enrichment, and correlation",
                "Alert triage, escalation, and incident response orchestration",
                "Vulnerability lifecycle and remediation tracking",
            ],
            "suggestions": [
                "Design deterministic severity scoring and response runbooks.",
                "Use tenant-aware isolation for logs, detections, and response actions.",
            ],
        },
    ),
    (
        ["climate", "carbon", "esg", "sustainability", "emissions"],
        {
            "label": "Climate / ESG",
            "capabilities": [
                "Emissions data ingestion and normalization pipelines",
                "Supplier/facility reporting and disclosure workflows",
                "Target tracking and audit-ready sustainability dashboards",
            ],
            "suggestions": [
                "Version methodologies for emissions calculations and reporting factors.",
                "Track data provenance for every ESG metric and disclosure artifact.",
            ],
        },
    ),
    (
        ["adtech", "ads", "campaign", "attribution", "marketing"],
        {
            "label": "AdTech",
            "capabilities": [
                "Campaign management and targeting controls",
                "Attribution and conversion measurement pipelines",
                "Budget pacing and fraud detection",
            ],
            "suggestions": [
                "Separate serving, measurement, and billing pipelines.",
                "Enforce consent-aware tracking and privacy controls.",
            ],
        },
    ),
]
