"""Compliance scanning file generators for Level 2 compliance documentation.

This module contains functions to generate compliance-specific scanning rules
and validation scripts for each supported framework (PCI-DSS, HIPAA, GDPR, etc.).
"""

from pathlib import Path
import html
import re
import time


MAX_SCAN_FILES = 400
MAX_FINDINGS_PER_RULE = 20
MAX_PATCHES_PER_RULE = 10
DEFAULT_PATCH_ALLOWLIST = ("src/", "app/", "services/")
DEFAULT_PATCH_DENYLIST = (
    "tests/",
    "test/",
    "node_modules/",
    "dist/",
    "build/",
)


def _localization_tokens(locale: str) -> dict[str, str]:
    lang = (locale or "en").strip().lower()
    tokens = {
        "es": {
            "Scanning & Validation": "Escaneo y Validacion",
            "Code Scanning Rules": "Reglas de Escaneo de Codigo",
            "Configuration Validation": "Validacion de Configuracion",
            "Remediation Path": "Ruta de Remediacion",
            "Patterns & Implementation Examples": "Patrones y Ejemplos de Implementacion",
            "Implementation Patterns": "Patrones de Implementacion",
            "Acceptance Criteria": "Criterios de Aceptacion",
            "Validation Checks": "Verificaciones de Validacion",
            "Notes": "Notas",
        },
        "fr": {
            "Scanning & Validation": "Analyse et Validation",
            "Code Scanning Rules": "Regles d Analyse du Code",
            "Configuration Validation": "Validation de Configuration",
            "Remediation Path": "Parcours de Remediation",
            "Patterns & Implementation Examples": "Modeles et Exemples d Implementation",
            "Implementation Patterns": "Modeles d Implementation",
            "Acceptance Criteria": "Criteres d Acceptation",
            "Validation Checks": "Verifications de Validation",
            "Notes": "Notes",
        },
    }
    return tokens.get(lang, {})


def _apply_locale(content: str, locale: str) -> str:
    localized = content
    for source, target in _localization_tokens(locale).items():
        localized = localized.replace(source, target)
    return localized


def _apply_region_variant(content: str, compliance_region: str | None) -> str:
    region = (compliance_region or "").strip().lower()
    if not region:
        return content
    labels = {
        "eu": "EU regional guidance",
        "us": "US regional guidance",
        "apac": "APAC regional guidance",
        "latam": "LATAM regional guidance",
    }
    title = labels.get(region, f"{region.upper()} regional guidance")
    return (
        content.rstrip()
        + "\n\n"
        + f"## Regional Variant\n- Region: {region.upper()}\n- Profile: {title}\n"
    )


def _localize_and_apply_region(
    files: dict[str, str], locale: str, compliance_region: str | None
) -> dict[str, str]:
    adjusted = {}
    for path, content in files.items():
        localized = _apply_locale(content, locale)
        adjusted[path] = _apply_region_variant(localized, compliance_region)
    return adjusted


def generate_level_2_compliance_scanning(
    compliance_packs: list[dict],
    locale: str = "en",
    compliance_region: str | None = None,
) -> dict[str, str]:
    """Generate Level 2 compliance scanning rules and validation scripts."""
    files = {}

    # PCI-DSS scanning rules
    pci_packs = [p for p in compliance_packs if p.get("key") == "pci-dss"]
    if pci_packs:
        files[".specs/compliance/pci-dss-scanning.md"] = """---
title: PCI-DSS Scanning & Validation Rules
type: compliance-scanning
tags: [compliance, pci-dss, scanning, security]
related:
  - [[.specs/memory.md]]
---

# PCI-DSS: Scanning & Validation (Level 2)

Automated scanning rules and validation for payment security.

## Code Scanning Rules

### Rule: Plaintext Secrets in Code
- Search: regex patterns for hardcoded passwords, API keys, tokens
- Tools: `truffleHog`, `detect-secrets`, `gitleaks`
- Command: `gitleaks detect --source git --verbose`
- Fail: Any match found
- Exception: Test data marked with `@test-only` comments

### Rule: Encryption Algorithm Validation
- Search: `malloc`, `strcpy`, `md5`, `sha1` (weak hashing)
- Tools: `semgrep`, `sonarqube`
- Command: `semgrep --config=p/security-audit --json`
- Fail: Weak crypto detected in production code
- Exception: Legacy compatibility layer with deprecation notice

### Rule: SQL Injection Risk Patterns
- Search: Raw SQL concatenation without parameterization
- Tools: `sqlcheck`, `semgrep`
- Command: `semgrep --config=p/owasp-top-ten`
- Fail: Unparameterized queries in user-input handling paths
- Exception: Schema migrations (pre-approved)

## Configuration Validation

### Checklist
- [ ] TLS 1.2+ enforced for all cardholder data connections
- [ ] Certificate pinning implemented for API clients
- [ ] HSTS headers set (min-age: 31536000)
- [ ] CSP headers restrict inline scripts
- [ ] Session cookies marked Secure + HttpOnly + SameSite=Strict

### Validation Script
```bash
#!/bin/bash
# Check TLS version
openssl s_client -connect $HOST:443 -tls1_2 &>/dev/null || echo "FAIL: TLS 1.2 not supported"

# Check HSTS header
curl -I https://$HOST | grep -i "strict-transport-security" || echo "FAIL: HSTS missing"

# Check CSP header
curl -I https://$HOST | grep -i "content-security-policy" || echo "WARN: CSP missing"
```

## Dependency Audit Commands

### Pre-Commit
```bash
npm audit --audit-level=moderate
pip install safety && safety check
composer audit
```

### CI/CD Pipeline
```bash
# Node.js
npm ci && npm audit --production

# Python
pip install pip-audit && pip-audit

# Ruby
bundle audit check --update
```

### Incident Response
```bash
# Find vulnerable dependency usage
npm ls vulnerable-package
grep -r "vulnerable-package" src/

# Force audit on specific package
npm view vulnerable-package vulnerabilities
```

## Remediation Path
1. Scan code nightly and on every PR
2. Block merge if FAIL rules detected
3. Escalate HIGH/CRITICAL findings to security team
4. Document exceptions in compliance log
5. Re-scan after remediation
"""

    # HIPAA scanning rules (abbreviated for space)
    hipaa_packs = [p for p in compliance_packs if p.get("key") == "hipaa"]
    if hipaa_packs:
        files[".specs/compliance/hipaa-scanning.md"] = """---
title: HIPAA Scanning & Validation Rules
type: compliance-scanning
tags: [compliance, hipaa, scanning, security]
related:
  - [[.specs/memory.md]]
---

# HIPAA: Scanning & Validation (Level 2)

Automated scanning for PHI protection and audit logging.

## Code Scanning Rules

### Rule: PHI Data Exposure
- Search: PHI patterns (SSN, MRN, DOB) logged without redaction
- Tools: `semgrep`, custom regex scanner
- Command: `grep -r "\\\\d{{3}}-\\\\d{{2}}-\\\\d{{4}}" src/ --include="*.py" --include="*.js"`
- Fail: Unredacted PHI in logs or error messages
- Exception: Audit log with encrypted storage

## Remediation Path
1. Scan on every commit and nightly
2. Immediate escalation for PHI exposure
3. Incident response team notified
"""

    # GDPR, SOC2, CCPA, ISO27001 scanning rules (simplified)
    for framework_key, framework_name in [
        ("gdpr", "GDPR"),
        ("soc2", "SOC2"),
        ("ccpa", "CCPA/CPRA"),
        ("iso27001", "ISO 27001"),
    ]:
        packs = [p for p in compliance_packs if p.get("key") == framework_key]
        if packs:
            files[f".specs/compliance/{framework_key}-scanning.md"] = f"""---
title: {framework_name} Scanning & Validation Rules
type: compliance-scanning
tags: [compliance, {framework_key}, scanning, security]
related:
  - [[.specs/memory.md]]
---

# {framework_name}: Scanning & Validation (Level 2)

Automated scanning for {framework_name} compliance.

## Code Scanning Rules

Refer to compliance pack guidelines for specific rules and remediation paths.

## Configuration Validation

See compliance framework documentation for validation checklists.

## Remediation Path

1. Identify findings
2. Create tickets for remediation
3. Track resolution
4. Re-scan after fixes
5. Document in compliance log
"""

    return _localize_and_apply_region(files, locale, compliance_region)


def generate_level_3_compliance_patterns(
    compliance_packs: list[dict],
    locale: str = "en",
    compliance_region: str | None = None,
) -> dict[str, str]:
    """Generate Level 3 implementation pattern examples."""
    files = {}

    pci_packs = [p for p in compliance_packs if p.get("key") == "pci-dss"]
    if pci_packs:
        files[".specs/compliance/pci-dss-patterns.md"] = """---
title: PCI-DSS Implementation Patterns
type: compliance-patterns
tags: [compliance, pci-dss, patterns, implementation]
related:
  - [[.specs/memory.md]]
  - [[.specs/compliance/pci-dss-scanning.md]]
---

# PCI-DSS: Patterns & Implementation Examples (Level 3)

Production-ready examples for secure payment handling.

## Pattern 1: Tokenize Card Data at Ingress

### Python (FastAPI)
```python
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/payments/tokenize")
async def tokenize_card(payload: dict):
    pan = payload.get("pan", "")
    cvv = payload.get("cvv", "")
    if not pan or not cvv:
        raise HTTPException(status_code=400, detail="Missing card data")

    token = payment_gateway.tokenize(pan=pan, cvv=cvv)
    # Never persist raw PAN or CVV.
    return {"card_token": token, "last4": pan[-4:]}
```

### Node.js (Express)
```javascript
app.post('/payments/tokenize', async (req, res) => {
  const { pan, cvv } = req.body;
  if (!pan || !cvv) return res.status(400).json({ error: 'Missing card data' });

  const token = await paymentGateway.tokenize({ pan, cvv });
  return res.json({ cardToken: token, last4: pan.slice(-4) });
});
```

### Go (net/http)
```go
func TokenizeCard(w http.ResponseWriter, r *http.Request) {
    var req struct { PAN string `json:"pan"`; CVV string `json:"cvv"` }
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid payload", http.StatusBadRequest)
        return
    }
    if req.PAN == "" || req.CVV == "" {
        http.Error(w, "missing card data", http.StatusBadRequest)
        return
    }

    token := paymentGateway.Tokenize(req.PAN, req.CVV)
    _ = json.NewEncoder(w).Encode(map[string]string{"cardToken": token, "last4": req.PAN[len(req.PAN)-4:]})
}
```

## Pattern 2: Encryption at Rest for Payment Metadata

### Python
```python
def store_payment_metadata(order_id: str, card_token: str, customer_id: str):
    encrypted = kms_encrypt_json(
        {
            "card_token": card_token,
            "customer_id": customer_id,
        },
        key_alias="alias/payments",
    )
    db.execute(
        "INSERT INTO payment_metadata(order_id, encrypted_blob) VALUES (%s, %s)",
        [order_id, encrypted],
    )
```

## Pattern 3: Structured Audit Trail (No Sensitive Values)

```json
{
  "event": "payment_authorized",
  "actor": "service:checkout-api",
  "order_id": "ord_12345",
  "card_last4": "4242",
  "result": "approved",
  "trace_id": "trace-abc-123"
}
```

## Acceptance Criteria
1. PAN and CVV are not persisted or logged.
2. Only gateway-issued tokens are stored in application systems.
3. Payment metadata is encrypted at rest with managed keys.
4. Audit logs are immutable and redact sensitive fields.

## Validation Checks
- Run `gitleaks detect --source .` on each pull request.
- Block deploy if static analysis finds weak cryptography or SQL injection paths.
- Verify production logs contain no PAN/CVV patterns.

## Notes
- Keep gateway credentials in a secrets manager.
- Rotate encryption keys and validate decryption in disaster recovery drills.
"""

    hipaa_packs = [p for p in compliance_packs if p.get("key") == "hipaa"]
    if hipaa_packs:
        files[".specs/compliance/hipaa-patterns.md"] = """---
title: HIPAA Implementation Patterns
type: compliance-patterns
tags: [compliance, hipaa, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/hipaa-scanning.md]]
---

# HIPAA: Patterns & Implementation Examples (Level 3)

Reference patterns for protecting PHI and preserving auditability.

## Pattern 1: PHI Redaction in Logs

```python
import re

SSN_RE = re.compile(r"\\b\\d{3}-\\d{2}-\\d{4}\\b")

def redact_phi(value: str) -> str:
        return SSN_RE.sub("***-**-****", value)

def safe_log(message: str) -> None:
        logger.info(redact_phi(message))
```

## Pattern 2: Access Checks Before PHI Read

```python
def fetch_patient_record(patient_id: str, actor: User):
        if not rbac.can(actor, "patient.read", patient_id):
                raise PermissionError("Access denied")
        return patient_repo.get(patient_id)
```

## Pattern 3: Immutable Audit Event

```json
{
    "event": "phi_record_accessed",
    "actor": "user:clinician-42",
    "patient_id": "pt_9012",
    "purpose": "treatment",
    "trace_id": "trace-hipaa-001"
}
```

## Acceptance Criteria
1. PHI fields are redacted from application logs.
2. PHI reads require explicit authorization checks.
3. Access events are logged with actor, purpose, and trace metadata.
"""

    gdpr_packs = [p for p in compliance_packs if p.get("key") == "gdpr"]
    if gdpr_packs:
        files[".specs/compliance/gdpr-patterns.md"] = """---
title: GDPR Implementation Patterns
type: compliance-patterns
tags: [compliance, gdpr, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/gdpr-scanning.md]]
---

# GDPR: Patterns & Implementation Examples (Level 3)

Reference patterns for consent, minimization, and deletion workflows.

## Pattern 1: Consent Gate for Optional Processing

```typescript
function canRunMarketingProfile(user: User): boolean {
    return user.consent?.marketing === true;
}
```

## Pattern 2: Data Minimization in API Response

```typescript
function toPublicUser(u: UserRecord) {
    return {
        id: u.id,
        displayName: u.displayName,
    };
}
```

## Pattern 3: Right-to-Erasure Job

```python
def erase_user_data(user_id: str):
        user_repo.delete_profile(user_id)
        event_repo.delete_by_user(user_id)
        object_storage.delete_prefix(f"users/{user_id}/")
```

## Acceptance Criteria
1. Optional processing requires explicit consent flags.
2. APIs return only data required for the current purpose.
3. Deletion workflows remove data from primary and derived stores.
"""

    soc2_packs = [p for p in compliance_packs if p.get("key") == "soc2"]
    if soc2_packs:
        files[".specs/compliance/soc2-patterns.md"] = """---
title: SOC2 Implementation Patterns
type: compliance-patterns
tags: [compliance, soc2, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/soc2-scanning.md]]
---

# SOC2: Patterns & Implementation Examples (Level 3)

Reference patterns for access control, change logging, and service reliability.

## Pattern 1: Role-Based Action Guard

```python
def require_role(user: User, role: str) -> None:
        if role not in user.roles:
                raise PermissionError(f"Missing role: {role}")
```

## Pattern 2: Change Audit Event

```json
{
    "event": "config_changed",
    "actor": "user:ops-admin-7",
    "resource": "billing.service.timeout",
    "old": "20s",
    "new": "30s",
    "ticket": "CHG-2419"
}
```

## Pattern 3: Health Check Contract

```typescript
app.get('/healthz', (_req, res) => {
    res.status(200).json({ status: 'ok', version: process.env.RELEASE_SHA });
});
```

## Acceptance Criteria
1. Privileged actions enforce explicit role checks.
2. Security-relevant configuration changes are audit logged.
3. Service health endpoints provide deterministic readiness signals.
"""

    ccpa_packs = [p for p in compliance_packs if p.get("key") == "ccpa"]
    if ccpa_packs:
        files[".specs/compliance/ccpa-patterns.md"] = """---
title: CCPA/CPRA Implementation Patterns
type: compliance-patterns
tags: [compliance, ccpa, cpra, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/ccpa-scanning.md]]
---

# CCPA/CPRA: Patterns & Implementation Examples (Level 3)

Reference patterns for consumer rights handling and sale/share controls.

## Pattern 1: Do-Not-Sell Enforcement

```typescript
function canShareForAds(profile: ConsumerProfile): boolean {
    return profile.optOutSaleShare !== true;
}
```

## Pattern 2: Consumer Request Export

```python
def export_consumer_data(consumer_id: str) -> dict:
        return {
                "profile": profile_repo.get(consumer_id),
                "events": event_repo.list_by_consumer(consumer_id),
                "preferences": pref_repo.get(consumer_id),
        }
```

## Pattern 3: Consumer Deletion Ticket

```json
{
    "event": "consumer_deletion_requested",
    "consumer_id": "c_1827",
    "request_id": "dsr-9921",
    "status": "queued"
}
```

## Acceptance Criteria
1. Ad-tech sharing is disabled when consumer opts out.
2. Access/export responses include all required consumer data categories.
3. Deletion requests are tracked from intake through completion.
"""

    iso_packs = [p for p in compliance_packs if p.get("key") == "iso27001"]
    if iso_packs:
        files[".specs/compliance/iso27001-patterns.md"] = """---
title: ISO27001 Implementation Patterns
type: compliance-patterns
tags: [compliance, iso27001, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/iso27001-scanning.md]]
---

# ISO 27001: Patterns & Implementation Examples (Level 3)

Reference patterns for control ownership, risk treatment, and incident readiness.

## Pattern 1: Control Ownership Registry

```yaml
controls:
    A.8.2:
        owner: security-platform
        evidence: s3://evidence/asset-classification/
    A.12.4:
        owner: sre
        evidence: s3://evidence/logging-monitoring/
```

## Pattern 2: Risk Register Entry

```json
{
    "risk_id": "R-117",
    "asset": "customer-data-api",
    "likelihood": "medium",
    "impact": "high",
    "treatment": "enable WAF + stricter rate limits",
    "owner": "platform-security"
}
```

## Pattern 3: Incident Runbook Trigger

```bash
#!/usr/bin/env bash
set -euo pipefail
incidentctl create --severity high --service customer-data-api --summary "Potential data exposure"
```

## Acceptance Criteria
1. Controls have defined owners and retrievable evidence links.
2. Risks include treatment plans and accountable owners.
3. Security incidents can be raised with a standardized, repeatable workflow.
"""

    return _localize_and_apply_region(files, locale, compliance_region)


LEVEL3_PATTERN_RULES = {
    "pci-dss": [
        {
            "id": "pci-weak-hash",
            "title": "Weak hashing algorithm usage",
            "pattern": r"\b(md5|sha1)\s*\(",
            "remediation": "Replace weak hashes with SHA-256 or stronger; prefer password_hash/argon2/bcrypt for credentials.",
            "snippet": "hashlib.sha256(value.encode('utf-8')).hexdigest()",
            "replacement_map": {
                "md5(": "sha256(",
                "sha1(": "sha256(",
            },
        },
        {
            "id": "pci-raw-sql",
            "title": "Potential raw SQL string interpolation",
            "pattern": r"(SELECT|INSERT|UPDATE|DELETE).*(\+|%\s*\()",
            "remediation": "Use parameterized queries in all data-access paths.",
            "snippet": "cursor.execute('SELECT * FROM users WHERE id = %s', [user_id])",
        },
    ],
    "hipaa": [
        {
            "id": "hipaa-possible-phi-log",
            "title": "Potential PHI logging",
            "pattern": r"(logger\.(info|debug|warning)|print\().*(ssn|dob|patient|mrn)",
            "remediation": "Redact PHI fields before logging and route audit events to controlled sinks.",
            "snippet": "logger.info(redact_phi(message))",
        }
    ],
    "gdpr": [
        {
            "id": "gdpr-marketing-without-consent",
            "title": "Marketing/profile path without explicit consent check",
            "pattern": r"(marketing|ads|profile).*(send|process|share)",
            "remediation": "Gate optional processing behind explicit consent flags.",
            "snippet": "if user.consent.get('marketing') is True:\n    run_marketing_profile(user)",
        }
    ],
    "soc2": [
        {
            "id": "soc2-missing-audit-trail",
            "title": "Privileged action without explicit audit event",
            "pattern": r"(delete_user|grant_role|rotate_key|change_config)\s*\(",
            "remediation": "Emit structured audit events for privileged operations.",
            "snippet": "audit.log({'event': 'config_changed', 'actor': actor_id, 'resource': resource})",
        }
    ],
    "ccpa": [
        {
            "id": "ccpa-share-without-optout",
            "title": "Data-sharing path may ignore do-not-sell/opt-out",
            "pattern": r"(share|sell).*(consumer|profile|data)",
            "remediation": "Enforce opt-out checks before any sale/share path.",
            "snippet": "if not profile.opt_out_sale_share:\n    share_data(profile)",
        }
    ],
    "iso27001": [
        {
            "id": "iso-no-incident-trigger",
            "title": "Security-sensitive code path without incident/runbook trigger",
            "pattern": r"(security_breach|data_exposure|critical_alert)",
            "remediation": "Tie high-severity detections to standardized incident runbook automation.",
            "snippet": "incidentctl create --severity high --service api --summary 'Potential exposure'",
        }
    ],
}


def _iter_source_files(project_dir: Path, max_files: int = 200) -> list[Path]:
    allowed = {".py", ".js", ".ts", ".tsx", ".go", ".java", ".rb", ".php"}
    ignored = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
    files: list[Path] = []

    bounded_max = max(1, min(int(max_files or 1), MAX_SCAN_FILES))

    for path in project_dir.rglob("*"):
        if len(files) >= bounded_max:
            break
        if any(part in ignored for part in path.parts):
            continue
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        files.append(path)

    return files


def generate_level_3_pattern_injection_report(
    project_dir: Path,
    compliance_packs: list[dict],
    max_findings_per_rule: int = 5,
) -> str | None:
    """Analyze project source for compliance risk patterns and propose remediation snippets."""
    findings = _collect_pattern_findings(
        project_dir,
        compliance_packs,
        max_findings_per_rule,
    )
    if not findings:
        return None

    lines = [
        "# Level 3 Code Pattern Injection Report",
        "",
        "Detected potential compliance risk patterns in source code and suggested remediation snippets.",
        "",
        "## Findings",
    ]

    for index, item in enumerate(findings, start=1):
        rel_path = str(item["path"].relative_to(project_dir))
        lines.extend(
            [
                f"### {index}. {item['framework'].upper()} - {item['title']}",
                f"- Rule: `{item['rule_id']}`",
                f"- Location: `{rel_path}:{item['line_no']}`",
                f"- Matched line: `{item['line']}`",
                f"- Remediation: {item['remediation']}",
                "- Suggested snippet:",
                "```",
                item["snippet"],
                "```",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _collect_pattern_findings(
    project_dir: Path,
    compliance_packs: list[dict],
    max_findings_per_rule: int,
) -> list[dict]:
    bounded_findings = max(
        1, min(int(max_findings_per_rule or 1), MAX_FINDINGS_PER_RULE)
    )
    deadline = time.monotonic() + 6.0
    source_files = _iter_source_files(project_dir)
    if not source_files:
        return []

    findings: list[dict] = []
    selected_keys = [pack.get("key") for pack in compliance_packs if pack.get("key")]

    for key in selected_keys:
        rules = LEVEL3_PATTERN_RULES.get(key, [])
        for rule in rules:
            compiled = re.compile(rule["pattern"], re.IGNORECASE)
            match_count = 0
            for src in source_files:
                if match_count >= bounded_findings or time.monotonic() > deadline:
                    break
                try:
                    content = src.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for line_no, line in enumerate(content.splitlines(), start=1):
                    if compiled.search(line):
                        findings.append(
                            {
                                "framework": key,
                                "rule_id": rule["id"],
                                "title": rule["title"],
                                "path": src,
                                "line_no": line_no,
                                "line": line.strip()[:160],
                                "remediation": rule["remediation"],
                                "snippet": rule["snippet"],
                            }
                        )
                        match_count += 1
                        break

    return findings


def generate_ai_assisted_compliance_analysis(
    project_dir: Path,
    compliance_packs: list[dict],
) -> str | None:
    """Generate heuristic AI-style risk analysis and architecture recommendations."""
    findings = _collect_pattern_findings(project_dir, compliance_packs, 10)
    if not findings:
        return None

    severity_by_framework = {
        "pci-dss": 9,
        "hipaa": 9,
        "gdpr": 8,
        "soc2": 7,
        "ccpa": 7,
        "iso27001": 6,
    }
    recommendation_by_framework = {
        "pci-dss": "Isolate payment handling into a dedicated service boundary with strict tokenization and parameterized DB access.",
        "hipaa": "Introduce a centralized privacy layer for PHI redaction and audited access policies.",
        "gdpr": "Add a consent-orchestration module and enforce purpose-scoped data views.",
        "soc2": "Route privileged actions through a policy gateway that emits immutable audit events.",
        "ccpa": "Implement a consumer-preference service that gates all sale/share pathways.",
        "iso27001": "Adopt a control-ownership and incident-workflow automation plane tied to runtime signals.",
    }

    framework_counts: dict[str, int] = {}
    for item in findings:
        fw = item["framework"]
        framework_counts[fw] = framework_counts.get(fw, 0) + 1

    weighted = 0
    for fw, count in framework_counts.items():
        weighted += severity_by_framework.get(fw, 5) * count
    risk_score = min(100, weighted)

    prioritized_frameworks = sorted(
        framework_counts.keys(),
        key=lambda fw: (
            -framework_counts.get(fw, 0),
            -severity_by_framework.get(fw, 5),
            fw,
        ),
    )

    lines = [
        "# AI-Assisted Compliance Analysis",
        "",
        "Heuristic risk analysis generated from detected compliance patterns and rule matches.",
        "",
        "## Risk Summary",
        f"- Aggregate risk score: {risk_score}/100",
        f"- Total findings: {len(findings)}",
        "",
        "## Framework Risk Breakdown",
    ]

    for fw in prioritized_frameworks:
        lines.append(
            f"- {fw.upper()}: {framework_counts[fw]} finding(s), baseline severity {severity_by_framework.get(fw, 5)}/10"
        )

    lines.extend(["", "## Recommended Architecture Changes"])
    for fw in prioritized_frameworks:
        lines.append(
            f"- {fw.upper()}: {recommendation_by_framework.get(fw, 'Harden service boundaries and observability around compliance-critical paths.')}"
        )

    lines.extend(["", "## Top Risk Signals"])
    for item in findings[:8]:
        rel_path = str(item["path"].relative_to(project_dir))
        lines.append(
            f"- {item['framework'].upper()} `{item['rule_id']}` at `{rel_path}:{item['line_no']}` -> {item['remediation']}"
        )

    return "\n".join(lines).rstrip() + "\n"


def generate_compliance_dashboard_html(
    project_dir: Path,
    compliance_packs: list[dict],
    planned_output_paths: list[str] | None = None,
) -> str:
    """Generate a static compliance dashboard for status, progress, and scan insights."""
    findings = _collect_pattern_findings(project_dir, compliance_packs, 20)
    frameworks = [str(pack.get("key") or "").strip() for pack in compliance_packs]
    frameworks = [fw for fw in frameworks if fw]

    planned_paths = planned_output_paths or []
    planned_compliance = [
        p for p in planned_paths if p.startswith(".specs/compliance/")
    ]
    existing_compliance_files = list(
        (project_dir / ".specs" / "compliance").rglob("*.md")
    )
    generated_count = len(existing_compliance_files)
    planned_count = max(len(planned_compliance), generated_count)
    progress_pct = (
        100
        if planned_count == 0
        else min(100, int((generated_count / planned_count) * 100))
    )

    framework_rows = []
    for fw in frameworks:
        fw_findings = [item for item in findings if item["framework"] == fw]
        status = "At Risk" if fw_findings else "No Signals"
        sev = "high" if len(fw_findings) >= 2 else ("medium" if fw_findings else "low")
        framework_rows.append(
            f"<tr><td>{html.escape(fw.upper())}</td><td>{status}</td><td>{sev}</td><td>{len(fw_findings)}</td></tr>"
        )

    finding_rows = []
    for item in findings[:25]:
        rel = str(item["path"].relative_to(project_dir))
        finding_rows.append(
            "<tr>"
            + f"<td>{html.escape(item['framework'].upper())}</td>"
            + f"<td>{html.escape(item['rule_id'])}</td>"
            + f"<td>{html.escape(rel)}:{item['line_no']}</td>"
            + f"<td>{html.escape(item['line'])}</td>"
            + "</tr>"
        )

    if not finding_rows:
        finding_rows.append(
            "<tr><td colspan='4'>No scan findings detected yet.</td></tr>"
        )

    framework_table = (
        "\n".join(framework_rows)
        if framework_rows
        else "<tr><td colspan='4'>No compliance frameworks selected.</td></tr>"
    )
    finding_table = "\n".join(finding_rows)

    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Compliance Dashboard</title>
    <style>
        :root {{
            --bg: #f4f7f5;
            --ink: #0f2a22;
            --accent: #0f766e;
            --panel: #ffffff;
            --warn: #b45309;
            --risk: #b91c1c;
        }}
        body {{ margin: 0; font-family: "Avenir Next", "Segoe UI", sans-serif; background: radial-gradient(circle at 80% 10%, #d8f5ef 0%, var(--bg) 48%); color: var(--ink); }}
        .wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
        .hero {{ background: linear-gradient(120deg, #0f766e, #115e59); color: #fff; padding: 22px; border-radius: 18px; box-shadow: 0 10px 30px rgba(0,0,0,.12); }}
        .meta {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 14px; margin-top: 18px; }}
        .card {{ background: var(--panel); border-radius: 14px; padding: 14px; box-shadow: 0 8px 22px rgba(0,0,0,.06); }}
        .bar {{ height: 12px; border-radius: 999px; background: #d1fae5; overflow: hidden; }}
        .bar > span {{ display:block; height: 100%; width: {progress_pct}%; background: linear-gradient(90deg, #14b8a6, #0f766e); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ text-align: left; padding: 9px 10px; border-bottom: 1px solid #e5e7eb; font-size: 14px; }}
        th {{ background: #f8fafc; }}
        .pulse {{ width: 10px; height: 10px; border-radius: 50%; background: #22c55e; display: inline-block; animation: pulse 1.6s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(1); opacity: 1; }} 100% {{ transform: scale(1.9); opacity: .15; }} }}
    </style>
</head>
<body>
    <div class=\"wrap\">
        <section class=\"hero\">
            <h1>Compliance Dashboard</h1>
            <p>Status visualization and scan telemetry for selected frameworks.</p>
            <p>Live scan status: <span class=\"pulse\"></span> <strong id=\"scan-state\">running</strong> · Last refresh <strong id=\"tick\">now</strong></p>
        </section>

        <section class=\"meta\">
            <article class=\"card\">
                <h3>Frameworks</h3>
                <p>{len(frameworks)} selected</p>
            </article>
            <article class=\"card\">
                <h3>Findings</h3>
                <p>{len(findings)} active signals</p>
            </article>
            <article class=\"card\">
                <h3>File Generation Progress</h3>
                <div class=\"bar\"><span></span></div>
                <p>{generated_count}/{planned_count} compliance files ({progress_pct}%)</p>
            </article>
        </section>

        <section class=\"card\" style=\"margin-top: 16px;\">
            <h3>Framework Status</h3>
            <table>
                <thead><tr><th>Framework</th><th>Status</th><th>Severity</th><th>Findings</th></tr></thead>
                <tbody>
                    {framework_table}
                </tbody>
            </table>
        </section>

        <section class=\"card\" style=\"margin-top: 16px;\">
            <h3>Real-Time Scanning Results</h3>
            <table>
                <thead><tr><th>Framework</th><th>Rule</th><th>Location</th><th>Matched Signal</th></tr></thead>
                <tbody>
                    {finding_table}
                </tbody>
            </table>
        </section>
    </div>
    <script>
        const tick = document.getElementById('tick');
        const scanState = document.getElementById('scan-state');
        function refreshClock() {{
            tick.textContent = new Date().toLocaleTimeString();
        }}
        setInterval(refreshClock, 1000);
        setInterval(() => {{
            scanState.textContent = scanState.textContent === 'running' ? 'streaming' : 'running';
        }}, 2400);
        refreshClock();
    </script>
</body>
</html>
"""


def _compute_patch_preview(
    line: str, replacement_map: dict[str, str] | None
) -> tuple[str, bool]:
    if not replacement_map:
        return line, False
    updated = line
    changed = False
    for source, target in replacement_map.items():
        if source in updated:
            updated = updated.replace(source, target)
            changed = True
    return updated, changed


def _collect_patch_candidates(
    project_dir: Path,
    compliance_packs: list[dict],
    max_candidates_per_rule: int,
) -> list[dict]:
    bounded_candidates = max(
        1, min(int(max_candidates_per_rule or 1), MAX_PATCHES_PER_RULE)
    )
    deadline = time.monotonic() + 6.0
    source_files = _iter_source_files(project_dir)
    if not source_files:
        return []

    selected_keys = [pack.get("key") for pack in compliance_packs if pack.get("key")]
    candidates: list[dict] = []

    for key in selected_keys:
        rules = LEVEL3_PATTERN_RULES.get(key, [])
        for rule in rules:
            compiled = re.compile(rule["pattern"], re.IGNORECASE)
            candidate_count = 0
            for src in source_files:
                if candidate_count >= bounded_candidates or time.monotonic() > deadline:
                    break
                try:
                    lines = src.read_text(
                        encoding="utf-8", errors="ignore"
                    ).splitlines()
                except Exception:
                    continue

                for line_no, raw_line in enumerate(lines, start=1):
                    if not compiled.search(raw_line):
                        continue
                    after_line, changed = _compute_patch_preview(
                        raw_line,
                        rule.get("replacement_map"),
                    )
                    if not changed:
                        continue
                    candidates.append(
                        {
                            "framework": key,
                            "rule_id": rule["id"],
                            "path": src,
                            "line_no": line_no,
                            "before": raw_line.rstrip(),
                            "after": after_line.rstrip(),
                        }
                    )
                    candidate_count += 1
                    break

    return candidates


def generate_level_3_patch_proposals(
    project_dir: Path,
    compliance_packs: list[dict],
    max_proposals_per_rule: int = 3,
) -> str | None:
    """Generate safe patch proposals (dry-run) for matched Level 3 compliance patterns."""
    proposals = _collect_patch_candidates(
        project_dir,
        compliance_packs,
        max_proposals_per_rule,
    )

    if not proposals:
        return None

    output = [
        "# Level 3 Auto-Patch Proposals (Dry-Run)",
        "",
        "Proposed non-destructive remediations based on detected compliance patterns.",
        "Apply manually after review.",
        "",
        "## Proposed Patches",
    ]

    for index, item in enumerate(proposals, start=1):
        rel_path = str(item["path"].relative_to(project_dir))
        output.extend(
            [
                f"### {index}. {item['framework'].upper()} - {item['rule_id']}",
                f"- File: `{rel_path}:{item['line_no']}`",
                "```diff",
                f"- {item['before']}",
                f"+ {item['after']}",
                "```",
                "",
            ]
        )

    return "\n".join(output).rstrip() + "\n"


def apply_level_3_patch_proposals(
    project_dir: Path,
    compliance_packs: list[dict],
    max_patches_per_rule: int = 3,
    patch_allowlist: list[str] | None = None,
    patch_denylist: list[str] | None = None,
) -> dict[str, list[dict]]:
    """Apply auto-patch replacements for candidates that have deterministic mappings."""
    applied: list[dict] = []
    candidates = _collect_patch_candidates(
        project_dir,
        compliance_packs,
        max_patches_per_rule,
    )

    allowlist = [
        value.strip().strip("/") + "/"
        for value in (patch_allowlist or list(DEFAULT_PATCH_ALLOWLIST))
        if value and value.strip()
    ]
    denylist = [
        value.strip().strip("/") + "/"
        for value in (patch_denylist or list(DEFAULT_PATCH_DENYLIST))
        if value and value.strip()
    ]

    for item in candidates:
        path = item["path"]
        line_no = int(item["line_no"])
        rel_path = str(path.relative_to(project_dir)).replace("\\", "/")
        if allowlist and not any(rel_path.startswith(prefix) for prefix in allowlist):
            continue
        if any(rel_path.startswith(prefix) for prefix in denylist):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        if line_no < 1 or line_no > len(lines):
            continue
        original = lines[line_no - 1]
        before_clean = str(item["before"]).strip()
        after_clean = str(item["after"]).strip()
        if original.strip() != before_clean:
            continue
        updated, changed = _compute_patch_preview(
            original,
            {before_clean: after_clean},
        )
        if not changed or updated == original:
            continue
        lines[line_no - 1] = updated
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        applied.append(
            {
                "framework": item["framework"],
                "rule_id": item["rule_id"],
                "path": path,
                "line_no": line_no,
                "before": original.rstrip(),
                "after": updated.rstrip(),
            }
        )

    return {"applied": applied}


def generate_level_3_applied_patch_report(
    project_dir: Path,
    applied_items: list[dict],
) -> str | None:
    if not applied_items:
        return None

    output = [
        "# Level 3 Auto-Patch Results",
        "",
        "Applied deterministic compliance remediations (explicit apply-mode).",
        "",
        "## Applied Changes",
    ]
    for index, item in enumerate(applied_items, start=1):
        rel_path = str(item["path"].relative_to(project_dir))
        output.extend(
            [
                f"### {index}. {item['framework'].upper()} - {item['rule_id']}",
                f"- File: `{rel_path}:{item['line_no']}`",
                "```diff",
                f"- {item['before']}",
                f"+ {item['after']}",
                "```",
                "",
            ]
        )

    return "\n".join(output).rstrip() + "\n"
